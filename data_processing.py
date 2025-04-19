import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st

@st.cache_resource
def get_db_connection():
    return sqlite3.connect("database/ecommerce.db")

def preprocess_data():
    conn = get_db_connection()
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