from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime
import logging
import os
from pathlib import Path

from database import engine
from models import Base
from prediction import predict_demand
from products import router as products_router
from alerts import router as alerts_router
from users import router as users_router
from suppliers import router as suppliers_router
from expiry import router as expiry_router
from notifications import router as notifications_router
from dashboard import router as dashboard_router
from orders import router as orders_router
from supplier_workflow import router as supplier_workflow_router
from transactions import router as transactions_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create tables with error handling
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified successfully")
except Exception as e:
    logger.warning(f"Could not create database tables on startup: {e}")
    logger.info("The application will continue to run. Database tables will be created when first accessed.")

app = FastAPI(
    title="Smart Inventory Management System",
    description="Inventory management with stock prediction and automated alerts",
    version="1.0.0"
)

# Add security middleware
# app.add_middleware(HTTPSRedirectMiddleware)  # Enable in production only
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "testserver",
        "*.example.com",
        os.getenv("RENDER_EXTERNAL_HOSTNAME", "*.onrender.com"),
    ]
)

# Add CORS middleware for frontend communication (SECURE)
# In production with unified server, CORS is less critical since both are same-origin
# But we keep it for development flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Include all routers
app.include_router(users_router, tags=["Authentication"])
app.include_router(suppliers_router, tags=["Supplier"])
app.include_router(products_router, tags=["Products"])
app.include_router(alerts_router, tags=["Alerts"])
app.include_router(dashboard_router, tags=["Dashboard"])
app.include_router(expiry_router, tags=["Expiry Management"])
app.include_router(notifications_router, tags=["Notifications"])
app.include_router(orders_router, tags=["Orders"])
app.include_router(supplier_workflow_router)
app.include_router(transactions_router)


@app.get("/", include_in_schema=False)
async def root():
    """Serve the frontend SPA"""
    frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
    index_file = frontend_dist / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {
        "message": "Smart Inventory Management System API is running!",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/predictions/{product_id}")
def get_prediction(product_id: int, days: int = 7):
    try:
        predictions = predict_demand(product_id, days)
        return {
            "product_id": product_id,
            "days": days,
            "predictions": predictions
        }
    except ValueError as e:
        logger.warning(f"Prediction error for product {product_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {str(e)}")
        raise HTTPException(status_code=500, detail="Model file not found")
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Serve static files from frontend build
frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"

if frontend_dist.exists():
    logger.info(f"Mounting static files from {frontend_dist}")
    app.mount("/assets", StaticFiles(directory=frontend_dist / "assets", check_dir=False), name="assets")
    
    # Serve index.html for SPA routing (must be last route)
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        """Serve the frontend SPA - index.html for all non-API routes"""
        
        # Exclude API routes from SPA serving
        api_prefixes = [
            "supplier", "products", "users", "alerts", "dashboard", 
            "expiry", "notifications", "orders", "product", "reorder-decision", "reorder-decisions",
            "supplier-alert", "transactions", "health", "docs", "openapi.json", "predictions"
        ]
        
        # Check if this path starts with an API prefix
        path_parts = full_path.split("/")
        if path_parts and path_parts[0] in api_prefixes:
            # This is an API call that wasn't matched - return 404
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        index_file = frontend_dist / "index.html"
        
        # If the file exists in dist, serve it
        file_path = frontend_dist / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        
        # Otherwise serve index.html for SPA routing
        if index_file.exists():
            return FileResponse(index_file)
        
        # If no dist folder, return 404
        raise HTTPException(status_code=404, detail="Frontend not built. Run 'npm run build' in frontend folder")
else:
    logger.warning("Frontend dist folder not found. Frontend will not be served.")
    logger.info("To build the frontend, run: cd frontend && npm install && npm run build")