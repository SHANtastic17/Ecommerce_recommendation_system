import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import os

@st.cache_resource
def get_db_connection():
    # Construct absolute path to the database file
    db_path = os.path.join(os.path.dirname(__file__), "database", "ecommerce.db")

    # Optional: check if DB exists to avoid silent failure
    if not os.path.exists(db_path):
        st.error(f"Database file not found at: {db_path}")
        return None

    return sqlite3.connect(db_path)

def preprocess_data():
    conn = get_db_connection()
    if conn is None:
        return pd.DataFrame()  # return empty dataframe if DB connection fails

    df = pd.read_sql("SELECT * FROM products", conn)
    conn.close()
    
    # Calculate discount percentage
    df['discount_percentage'] = ((df['retail_price'] - df['discounted_price']) / df['retail_price']) * 100
    return df

def display_data_analysis(refined_df):
    """Display data analysis visualizations."""
    st.header("Data Analysis")

    # Price distribution visualization
    top_categories = refined_df['primary_category'].value_counts().nlargest(10).index
    top_categories_df = refined_df[refined_df['primary_category'].isin(top_categories)]

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.boxplot(x='retail_price', y='primary_category', data=top_categories_df, ax=ax)
    ax.set_title('Price Distribution Across Top Categories')
    st.pyplot(fig)

    # Discount percentage visualization
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(refined_df['discount_percentage'], bins=30, kde=True, ax=ax)
    ax.set_title('Discount Percentage Distribution')
    st.pyplot(fig)
