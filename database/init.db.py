import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))  # Add project root to path

from data_processing import extract_primary_category, extract_primary_image, determine_gender
import sqlite3
import pandas as pd
import os
import streamlit as st


def initialize_database():
    print("🔄 Initializing database...")
    conn = sqlite3.connect("database/ecommerce.db")
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            pid TEXT PRIMARY KEY,
            product_url TEXT,
            product_name TEXT,
            retail_price REAL,
            discounted_price REAL,
            description TEXT,
            brand TEXT,
            primary_image_link TEXT,
            gender TEXT,
            primary_category TEXT
        )
    """)

    # Load and insert data
    df = pd.read_csv("flipkart_com-ecommerce_sample.csv")
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT OR REPLACE INTO products VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
            )
        """, (
            row['pid'],
            row['product_url'],
            row['product_name'],
            row['retail_price'],
            row['discounted_price'],
            row['description'],
            row['brand'],
            extract_primary_image(row['image']),
            determine_gender(row['product_name'], row['description']),
            extract_primary_category(row['product_category_tree'])
        ))

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

if __name__ == "__main__":
    initialize_database()