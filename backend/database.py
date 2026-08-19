import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
from urllib.parse import quote

# Load environment variables
load_dotenv()

# Database configuration from environment variables (SECURE)
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "nikhil@143")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "smart_inventory")

# URL-encode the password to handle special characters (like @)
DB_PASSWORD_ENCODED = quote(DB_PASSWORD, safe='')

# Build database URL securely
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine with security and performance optimizations
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",  # Only echo if explicitly enabled
    poolclass=QueuePool,  # Connection pooling for performance
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600,  # Recycle connections every hour
    pool_pre_ping=True,  # Test connections before using
    connect_args={"charset": "utf8mb4"}  # Secure character encoding
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    """Get database session with proper error handling and cleanup"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()