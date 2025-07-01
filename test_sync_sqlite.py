#!/usr/bin/env python3

import sqlite3
import json

def test_sync_sqlite():
    """Test simple SQLite operations synchronously"""
    print("Testing simple SQLite...")
    
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    conn.commit()
    print("Table created")
    
    # Insert data
    test_data = json.dumps({"name": "Test Company", "active": True})
    cursor.execute("INSERT INTO companies (data) VALUES (?)", (test_data,))
    conn.commit()
    print("Data inserted")
    
    # Select data
    cursor.execute("SELECT id, data FROM companies")
    row = cursor.fetchone()
    if row:
        print(f"Found data: {row}")
        data = json.loads(row[1])
        print(f"Parsed JSON: {data}")
    else:
        print("No data found")
    
    conn.close()
    print("SQLite test completed successfully!")

if __name__ == "__main__":
    test_sync_sqlite()
