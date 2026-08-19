"""
Script to add comprehensive supplier data to the Smart Inventory System
"""

from database import SessionLocal
from models import Supplier
from auth import hash_password
from datetime import datetime, timedelta
import json

# Sample supplier data
SUPPLIERS_DATA = [
    # Electronics & Tech Supplies
    {
        "supplier_id": "sup_electronics_001",
        "email": "contact@techsupply.com",
        "company_name": "TechSupply Electronics",
        "contact_person": "Rajesh Kumar",
        "password": "TechSupply@2024",
        "phone": "+91-9876543210",
        "address": "123 Tech Park, Bangalore, India 560001",
        "gst_number": "18AABCT1234A1Z0",
        "is_approved": 1,
        "is_active": 1
    },
    {
        "supplier_id": "sup_electronics_002",
        "email": "sales@digitech.com",
        "company_name": "DigiTech Solutions",
        "contact_person": "Priya Singh",
        "password": "DigiTech@2024",
        "phone": "+91-9876543211",
        "address": "456 Innovation Hub, Hyderabad, India 500001",
        "gst_number": "36AABCS5678B1Z1",
        "is_approved": 1,
        "is_active": 1
    },
    # Food & Beverage Suppliers
    {
        "supplier_id": "sup_food_001",
        "email": "order@freshfoods.com",
        "company_name": "Fresh Foods Wholesale",
        "contact_person": "Amit Patel",
        "password": "FreshFood@2024",
        "phone": "+91-9876543212",
        "address": "789 Market Street, Delhi, India 110001",
        "gst_number": "07AABCT2345C1Z2",
        "is_approved": 1,
        "is_active": 1
    },
    {
        "supplier_id": "sup_food_002",
        "email": "supplies@organicmart.com",
        "company_name": "Organic Mart Ltd",
        "contact_person": "Neha Verma",
        "password": "OrganicMart@2024",
        "phone": "+91-9876543213",
        "address": "321 Green Road, Pune, India 411001",
        "gst_number": "27AABCT3456D1Z3",
        "is_approved": 1,
        "is_active": 1
    },
    # Pharmaceutical Suppliers
    {
        "supplier_id": "sup_pharma_001",
        "email": "sales@medhub.com",
        "company_name": "MedHub Pharmaceuticals",
        "contact_person": "Dr. Arjun Desai",
        "password": "MedHub@2024",
        "phone": "+91-9876543214",
        "address": "654 Medical Plaza, Mumbai, India 400001",
        "gst_number": "27AABCT4567E1Z4",
        "is_approved": 1,
        "is_active": 1
    },
    {
        "supplier_id": "sup_pharma_002",
        "email": "distribution@pharmalogistics.com",
        "company_name": "Pharma Logistics India",
        "contact_person": "Vikram Nair",
        "password": "PharmaLog@2024",
        "phone": "+91-9876543215",
        "address": "987 Chemical Zone, Gujarat, India 360001",
        "gst_number": "24AABCT5678F1Z5",
        "is_approved": 1,
        "is_active": 1
    },
    # Textile & Apparel Suppliers
    {
        "supplier_id": "sup_textile_001",
        "email": "inquiry@fabricworld.com",
        "company_name": "Fabric World",
        "contact_person": "Suresh Menon",
        "password": "Fabric@2024",
        "phone": "+91-9876543216",
        "address": "159 Textile Hub, Surat, India 395001",
        "gst_number": "24AABCT6789G1Z6",
        "is_approved": 1,
        "is_active": 1
    },
    {
        "supplier_id": "sup_textile_002",
        "email": "sales@clothcorp.com",
        "company_name": "Cloth Corporation",
        "contact_person": "Sneha Gupta",
        "password": "ClothCorp@2024",
        "phone": "+91-9876543217",
        "address": "753 Fashion District, Delhi, India 110002",
        "gst_number": "07AABCT7890H1Z7",
        "is_approved": 0,  # Pending approval
        "is_active": 1
    },
    # Hardware & Industrial Supplies
    {
        "supplier_id": "sup_hardware_001",
        "email": "contact@ironworks.com",
        "company_name": "Iron Works Ltd",
        "contact_person": "Rajesh Rao",
        "password": "IronWorks@2024",
        "phone": "+91-9876543218",
        "address": "246 Industrial Area, Chennai, India 600001",
        "gst_number": "33AABCT8901I1Z8",
        "is_approved": 1,
        "is_active": 1
    },
    {
        "supplier_id": "sup_hardware_002",
        "email": "sales@steelmart.com",
        "company_name": "Steel Mart Industries",
        "contact_person": "Hemant Joshi",
        "password": "SteelMart@2024",
        "phone": "+91-9876543219",
        "address": "135 Steel Zone, Jamshedpur, India 831001",
        "gst_number": "20AABCT9012J1Z9",
        "is_approved": 1,
        "is_active": 1
    },
    # Cosmetics & Personal Care
    {
        "supplier_id": "sup_cosmetics_001",
        "email": "biz@beautyplus.com",
        "company_name": "Beauty Plus Supplies",
        "contact_person": "Divya Sharma",
        "password": "BeautyPlus@2024",
        "phone": "+91-9876543220",
        "address": "369 Beauty Avenue, Bangalore, India 560002",
        "gst_number": "18AABCT0123K2Z0",
        "is_approved": 1,
        "is_active": 1
    },
    {
        "supplier_id": "sup_cosmetics_002",
        "email": "sales@naturals.com",
        "company_name": "Naturals Cosmetics",
        "contact_person": "Ananya Das",
        "password": "Naturals@2024",
        "phone": "+91-9876543221",
        "address": "741 Natural Park, Hyderabad, India 500002",
        "gst_number": "36AABCT1234L2Z1",
        "is_approved": 0,  # Pending approval
        "is_active": 1
    },
    # Packaging & Materials
    {
        "supplier_id": "sup_packaging_001",
        "email": "order@packright.com",
        "company_name": "PackRight Solutions",
        "contact_person": "Rohan Bhatia",
        "password": "PackRight@2024",
        "phone": "+91-9876543222",
        "address": "852 Packaging Park, Pune, India 411002",
        "gst_number": "27AABCT2345M2Z2",
        "is_approved": 1,
        "is_active": 1
    },
    {
        "supplier_id": "sup_packaging_002",
        "email": "supplies@boxworld.com",
        "company_name": "BoxWorld Enterprises",
        "contact_person": "Pooja Malhotra",
        "password": "BoxWorld@2024",
        "phone": "+91-9876543223",
        "address": "963 Box Street, Mumbai, India 400002",
        "gst_number": "27AABCT3456N2Z3",
        "is_approved": 1,
        "is_active": 1
    },
    # Agricultural Supplies
    {
        "supplier_id": "sup_agri_001",
        "email": "sales@agrisource.com",
        "company_name": "AgriSource India",
        "contact_person": "Prakash Yadav",
        "password": "AgriSource@2024",
        "phone": "+91-9876543224",
        "address": "147 Farm Lane, Madhya Pradesh, India 452001",
        "gst_number": "23AABCT4567O2Z4",
        "is_approved": 1,
        "is_active": 1
    },
    {
        "supplier_id": "sup_agri_002",
        "email": "contact@farmtech.com",
        "company_name": "FarmTech Solutions",
        "contact_person": "Arun Kumar",
        "password": "FarmTech@2024",
        "phone": "+91-9876543225",
        "address": "258 Agricultural Hub, Karnataka, India 560050",
        "gst_number": "29AABCT5678P2Z5",
        "is_approved": 0,  # Pending approval
        "is_active": 1
    },
    # Furniture & Home Furnishings
    {
        "supplier_id": "sup_furniture_001",
        "email": "sales@homestyle.com",
        "company_name": "HomeStyle Furniture",
        "contact_person": "Vikas Singh",
        "password": "HomeStyle@2024",
        "phone": "+91-9876543226",
        "address": "369 Furniture Plaza, Noida, India 201301",
        "gst_number": "09AABCT6789Q2Z6",
        "is_approved": 1,
        "is_active": 1
    },
    {
        "supplier_id": "sup_furniture_002",
        "email": "inquiry@designfurniture.com",
        "company_name": "Design Furniture Co",
        "contact_person": "Meena Reddy",
        "password": "DesignFurn@2024",
        "phone": "+91-9876543227",
        "address": "741 Design Lane, Telangana, India 500080",
        "gst_number": "36AABCT7890R2Z7",
        "is_approved": 1,
        "is_active": 1
    },
    # Automotive Supplies
    {
        "supplier_id": "sup_auto_001",
        "email": "sales@autoparts.com",
        "company_name": "Auto Parts Depot",
        "contact_person": "Sanjay Patel",
        "password": "AutoParts@2024",
        "phone": "+91-9876543228",
        "address": "852 Automotive Zone, Gujarat, India 360002",
        "gst_number": "24AABCT8901S2Z8",
        "is_approved": 1,
        "is_active": 1
    },
    {
        "supplier_id": "sup_auto_002",
        "email": "inquiry@vehicletech.com",
        "company_name": "VehicleTech Industries",
        "contact_person": "Rajiv Gupta",
        "password": "VehicleTech@2024",
        "phone": "+91-9876543229",
        "address": "963 Auto Hub, Maharashtra, India 440001",
        "gst_number": "27AABCT9012T2Z9",
        "is_approved": 0,  # Pending approval
        "is_active": 1
    },
]

def add_suppliers():
    """Add supplier data to the database"""
    db = SessionLocal()
    
    try:
        # Count existing suppliers
        existing_count = db.query(Supplier).count()
        print(f"🔍 Current suppliers in database: {existing_count}")
        
        added_count = 0
        skipped_count = 0
        
        for supplier_data in SUPPLIERS_DATA:
            # Check if supplier already exists
            existing = db.query(Supplier).filter(
                (Supplier.supplier_id == supplier_data["supplier_id"]) |
                (Supplier.email == supplier_data["email"])
            ).first()
            
            if existing:
                print(f"⏭️  Skipped: {supplier_data['company_name']} (already exists)")
                skipped_count += 1
                continue
            
            # Create new supplier
            new_supplier = Supplier(
                supplier_id=supplier_data["supplier_id"],
                email=supplier_data["email"],
                company_name=supplier_data["company_name"],
                contact_person=supplier_data["contact_person"],
                hashed_password=hash_password(supplier_data["password"]),
                phone=supplier_data["phone"],
                address=supplier_data["address"],
                gst_number=supplier_data["gst_number"],
                is_approved=supplier_data["is_approved"],
                is_active=supplier_data["is_active"]
            )
            
            db.add(new_supplier)
            added_count += 1
            
            status = "✅ Approved" if supplier_data["is_approved"] else "⏳ Pending"
            print(f"➕ Added: {supplier_data['company_name']} ({supplier_data['supplier_id']}) - {status}")
        
        # Commit all changes
        db.commit()
        
        # Get final count
        final_count = db.query(Supplier).count()
        
        print(f"\n{'='*60}")
        print(f"📊 Summary:")
        print(f"  • Added: {added_count} new suppliers")
        print(f"  • Skipped: {skipped_count} (already exist)")
        print(f"  • Total suppliers: {existing_count} → {final_count}")
        print(f"{'='*60}")
        
        # Show breakdown by approval status
        approved = db.query(Supplier).filter(Supplier.is_approved == 1).count()
        pending = db.query(Supplier).filter(Supplier.is_approved == 0).count()
        print(f"✅ Approved suppliers: {approved}")
        print(f"⏳ Pending suppliers: {pending}")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding suppliers: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Smart Inventory System - Supplier Data Insertion\n")
    add_suppliers()
