import sqlite3
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import streamlit as st
import os

def get_db_path():
    return os.path.join(os.path.dirname(__file__), "database", "ecommerce.db")

@st.cache_data(ttl=3600)
def preprocess_data():
    db_path = get_db_path()
    if not os.path.exists(db_path):
        st.error(f"Database file not found at: {db_path}")
        return pd.DataFrame()

    # Open the connection inside the function each time (no caching of conn)
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql("SELECT * FROM products", conn)

    df['discount_percentage'] = ((df['retail_price'] - df['discounted_price']) / df['retail_price']) * 100
    return df

def display_data_analysis(refined_df):
    st.header("Data Analysis")

    top_categories = refined_df['primary_category'].value_counts().nlargest(10).index
    top_categories_df = refined_df[refined_df['primary_category'].isin(top_categories)]

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.boxplot(x='retail_price', y='primary_category', data=top_categories_df, ax=ax)
    ax.set_title('Price Distribution Across Top Categories')
    st.pyplot(fig)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(refined_df['discount_percentage'], bins=30, kde=True, ax=ax)
    ax.set_title('Discount Percentage Distribution')
    st.pyplot(fig)
