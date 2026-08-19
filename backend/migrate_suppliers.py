"""
Migration script to add missing columns to suppliers table
"""
from sqlalchemy import text
from database import engine

def migrate():
    with engine.connect() as conn:
        # Get the existing columns
        result = conn.execute(text("DESCRIBE suppliers"))
        existing_columns = {row[0] for row in result}
        
        columns_to_add = {
            'contact_person': 'VARCHAR(150)',
            'phone': 'VARCHAR(20)',
            'address': 'TEXT',
            'gst_number': 'VARCHAR(50)',
            'updated_at': 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'
        }
        
        for col_name, col_def in columns_to_add.items():
            if col_name not in existing_columns:
                alter_query = f"ALTER TABLE suppliers ADD COLUMN {col_name} {col_def}"
                print(f"Adding column: {col_name}")
                conn.execute(text(alter_query))
                conn.commit()
            else:
                print(f"Column {col_name} already exists")

if __name__ == '__main__':
    migrate()
    print("Migration completed!")
