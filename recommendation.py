import os
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
# Securely load Gemini API key from Streamlit Secrets
try:
    genai.configure(api_key=st.secrets["api_keys"]["GEMINI_API_KEY"])
except Exception as e:
    st.error("Failed to configure Gemini API. Check your secrets configuration.")
    st.stop()

# Load API key from .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini API
genai.configure(api_key=api_key)

def generate_product_description(prompt):
    """
    Generate a product description using Gemini API based on a prompt.
    """
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating description: {str(e)}")
        return ""

def display_product_recommendation(refined_df):
    """
    Display product recommendation interface.
    """
    st.header("Product Recommendation")

    # Filter options
    category = st.selectbox("Select Category", sorted(refined_df['primary_category'].dropna().unique()))
    max_price = st.slider("Select Maximum Price", 
                         min_value=int(refined_df['discounted_price'].min()), 
                         max_value=int(refined_df['discounted_price'].max()), 
                         value=int(refined_df['discounted_price'].mean()))
    gender = st.selectbox("Select Gender", ["Unisex", "Men", "Women"])

    # Filter based on selections
    filtered_df = refined_df[
        (refined_df['primary_category'] == category) &
        (refined_df['discounted_price'] <= max_price) &
        (refined_df['gender'] == gender)
    ]

    if filtered_df.empty:
        st.warning("No products match the selected criteria.")
        return

    # Show recommended products
    st.subheader("Recommended Products")
    for _, row in filtered_df.head(5).iterrows():
        if row['primary_image_link']:
            st.image(row['primary_image_link'], width=200)
        st.markdown(f"**{row['product_name']}**")
        st.markdown(f"Brand: {row['brand']}")
        st.markdown(f"Price: ₹{row['discounted_price']} (Retail: ₹{row['retail_price']})")
        
        # Generate AI description
        if st.button(f"Generate AI Description for {row['pid']}", key=row['pid']):
            prompt = f"Write a short, attractive product description for: {row['product_name']}. Category: {row['primary_category']}, Brand: {row['brand']}."
            ai_description = generate_product_description(prompt)
            st.success(ai_description)