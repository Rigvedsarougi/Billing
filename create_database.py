import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('invoice_data.db')
cursor = conn.cursor()

# Create table to store invoice data
cursor.execute('''
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_date TEXT NOT NULL,
    customer_name TEXT NOT NULL,
    gst_number TEXT,
    contact_number TEXT,
    address TEXT,
    employee_name TEXT NOT NULL,
    discount_category TEXT NOT NULL,
    products TEXT NOT NULL,
    quantities TEXT NOT NULL,
    total_price REAL NOT NULL,
    tax_amount REAL NOT NULL,
    grand_total REAL NOT NULL
)
''')

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database and table created successfully.")
