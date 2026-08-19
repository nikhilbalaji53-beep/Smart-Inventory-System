# Smart Inventory Management System

A comprehensive full-stack inventory management system with stock prediction, automated alerts, and real-time monitoring.

## 🎯 Features

### 🔐 Authentication
- User registration and login with JWT tokens
- Secure password hashing with bcrypt
- Admin-based access control

### 📦 Inventory Management
- Add, update, and delete products
- Track current stock levels
- Set minimum stock thresholds
- Monitor inventory value
- Categorize products

### 📊 Stock Monitoring
- Real-time stock level tracking
- Automatic low-stock alerts
- Reorder quantity recommendations
- Stock prediction based on historical data

### 🟠 Expiry Management
- Track product expiration dates
- Separate alerts for expiring and expired products
- Filter products by expiry status
- Days until expiry calculations

### 🔮 Demand Forecasting
- 7-day demand predictions using Random Forest ML model
- Historical sales data analysis
- Trend-based forecasting

### 📈 Smart Dashboard
- Real-time inventory metrics
- Alert visualization
- Low stock product list
- Expiry status overview
- Inventory value calculation
- 7-day demand forecast

### ⚠️ Alert System
- **Low Stock Alerts**: When inventory falls below minimum threshold
- **Expiry Alerts**: When products are expiring soon or expired
- **Demand Alerts**: When predicted demand exceeds current stock
- Priority-based severity (Critical/Warning)
- Reorder recommendations

## 🏗️ Project Structure

```
Smart-Inventory-System/
├── backend/
│   ├── main.py              # FastAPI app entry point
│   ├── auth.py              # Authentication & JWT handling
│   ├── users.py             # User management routes
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic validation schemas
│   ├── database.py          # Database configuration
│   ├── products.py          # Product management routes
│   ├── alerts.py            # Stock alert logic
│   ├── expiry.py            # Expiry monitoring routes
│   ├── dashboard.py         # Dashboard metrics routes
│   ├── prediction.py        # Demand prediction logic
│   ├── requirements.txt     # Python dependencies
│   └── ...
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main app component
│   │   ├── App.css          # App styling
│   │   ├── Login.jsx        # Login/Register component
│   │   ├── Login.css        # Login styling
│   │   ├── Dashboard.jsx    # Main dashboard
│   │   ├── Dashboard.css    # Dashboard styling
│   │   ├── ProductList.jsx  # Product inventory table
│   │   ├── ProductList.css  # Product list styling
│   │   ├── AddProduct.jsx   # Add product form
│   │   ├── AddProduct.css   # Add product styling
│   │   ├── Alerts.jsx       # Alerts & notifications
│   │   ├── Alerts.css       # Alerts styling
│   │   ├── api.js           # API client
│   │   ├── main.jsx         # React entry point
│   │   └── index.css        # Global styles
│   ├── package.json         # NPM dependencies
│   ├── vite.config.js       # Vite configuration
│   └── ...
├── ml/
│   ├── ml/
│   │   └── train_model.py   # Model training script
│   ├── dataset.csv          # Training data
│   ├── model.joblib         # Trained ML model
│   └── ...
└── README.md
```

## 🚀 Quick Start

### 🎯 Unified Server (Recommended - Frontend + Backend Together)

**Windows PowerShell:**
```powershell
.\setup.ps1        # One-time setup
.\run-server.ps1   # Start server
```

**Windows Command Prompt:**
```cmd
setup.bat          # One-time setup
run-server.bat     # Start server
```

Then open **http://localhost:8000** in your browser.

📖 **Detailed Guide**: See [UNIFIED_SERVER_SETUP.md](UNIFIED_SERVER_SETUP.md)  
⚡ **Quick Reference**: See [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

---

### Prerequisites
- Python 3.8+
- Node.js 16+
- MySQL 5.7+

### Backend Setup (Separate - For Development)

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Configure database:**
Update the database URL in `backend/database.py`:
```python
DATABASE_URL = "mysql+pymysql://root:your_password@localhost/smart_inventory"
```

3. **Create database:**
```sql
CREATE DATABASE smart_inventory;
```

4. **Run the server:**
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Frontend Setup (Separate - For Development)

1. **Install dependencies:**
```bash
cd frontend
npm install
```

2. **Run development server:**
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## 📱 Using the Application

### 1. Login/Register
- Create a new account or login with existing credentials
- Admin accounts have full access

### 2. Dashboard Overview
- View key metrics: Total Products, Total Stock, Inventory Value
- See active alerts (Low Stock, Expiring Soon, Expired)
- Monitor 7-day demand forecast

### 3. Manage Products
- **Add Product**: Click "Add Product" tab, fill in details
- **View Products**: "Products" tab shows all inventory
- **Edit Product**: Click edit button (✏️) on any product row
- **Update Stock**: Click stock button (📦) to modify quantities
- **Delete Product**: Click delete button (🗑️)

### 4. Monitor Alerts
- **Low Stock Alerts**: Products below minimum threshold
  - Shows current stock, minimum required, and deficit
  - Includes reorder quantity recommendation
- **Expiry Alerts**: Products expiring in next 7 days
- **Expired Products**: Already expired items marked for removal

### 5. Filter & Search
- Filter products by category
- View alerts by type
- Sort by expiry date, stock level

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user

### Products
- `GET /products/` - List all products
- `GET /products/{id}` - Get single product
- `POST /products/` - Create product
- `PUT /products/{id}` - Update product
- `PATCH /products/{id}/stock` - Update stock
- `DELETE /products/{id}` - Delete product

### Alerts
- `GET /alerts/` - Get stock alerts with reorder recommendations

### Expiry Monitoring
- `GET /expiry/alerts` - Get expiry alerts
- `GET /expiry/expiring-soon` - Products expiring in 7 days
- `GET /expiry/expired` - All expired products

### Dashboard
- `GET /dashboard/` - Quick metrics
- `GET /dashboard/summary` - Detailed summary with all alerts

### Predictions
- `GET /predictions/{product_id}` - Get demand forecast

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(50) UNIQUE NOT NULL,
  email VARCHAR(100) UNIQUE NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  is_admin INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Products Table
```sql
CREATE TABLE products (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  category VARCHAR(100),
  price DECIMAL(10, 2) NOT NULL,
  current_stock INT DEFAULT 0,
  minimum_stock INT DEFAULT 10,
  supplier VARCHAR(150),
  expiry_date DATE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🤖 Machine Learning Model

The prediction system uses a **Random Forest Regressor** trained on historical sales data.

**Features used:**
- `product_id`: Product identifier
- `day_of_year`: Day in the year (1-365)
- `month`: Month (1-12)
- `day_of_week`: Day of week (0-6)

**Model retraining:**
```bash
python ml/ml/train_model.py
```

## 🎨 UI/UX Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark/Light Themes**: Modern gradient-based UI
- **Real-time Updates**: Live dashboard metrics
- **Interactive Charts**: Alert visualization
- **Color-coded Alerts**: Easy identification of severity levels
- **Intuitive Navigation**: Tab-based interface

## 🔒 Security Features

- JWT token-based authentication
- Bcrypt password hashing
- CORS protection
- Input validation with Pydantic
- Secure database connections
- Protected API endpoints

## 🐛 Troubleshooting

### Backend Issues

**Database connection error:**
- Verify MySQL is running
- Check connection string in `database.py`
- Ensure database exists

**JWT errors:**
- Clear browser localStorage
- Login again
- Check token expiration time

### Frontend Issues

**Cannot connect to API:**
- Ensure backend is running on port 8000
- Check CORS settings in `main.py`
- Verify API base URL in `api.js`

**Page not loading:**
- Clear browser cache
- npm reinstall
- Restart dev server

## 📦 Dependencies

### Backend
- FastAPI - Web framework
- SQLAlchemy - ORM
- Pydantic - Data validation
- PyJWT - JWT tokens
- Passlib - Password hashing
- Scikit-learn - ML model
- Pandas - Data manipulation

### Frontend
- React 19 - UI library
- Vite - Build tool
- Fetch API - HTTP requests

## 🚀 Deployment

### Backend (Production)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

### Frontend (Production)
```bash
npm run build
# Serve the dist/ folder with a web server
```

## 📝 Future Enhancements

- [ ] Export inventory reports (PDF/Excel)
- [ ] Email notifications for alerts
- [ ] Multi-warehouse support
- [ ] Supplier management system
- [ ] Sales analytics dashboard
- [ ] Barcode scanning
- [ ] Mobile app
- [ ] Real-time WebSocket updates
- [ ] Advanced search and filtering
- [ ] Audit logs

## 📄 License

This project is licensed under the MIT License.

## 👨‍💼 Support

For issues, questions, or feature requests, please create an issue in the repository.

---

**Built with ❤️ using FastAPI, React, and Machine Learning**
"# Smart-Inventory-System" 
