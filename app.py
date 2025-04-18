import streamlit as st
from data_processing import load_data, preprocess_data, display_data_analysis
from recommendation import display_product_recommendation
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    st.title("E-commerce Product Recommendation System")
    st.sidebar.title("Navigation")
    
    # Load dataset
    dataset_path = "flipkart_com-ecommerce_sample.csv"
    df = load_data(dataset_path)
    
    if df is not None:
        refined_df = preprocess_data(df)
        
        app_mode = st.sidebar.selectbox(
            "Choose Mode", 
            ["Data Analysis", "Product Recommendation"]
        )
        
        if app_mode == "Data Analysis":
            display_data_analysis(refined_df)
        else:
            display_product_recommendation(refined_df)

if __name__ == "__main__":
    main()