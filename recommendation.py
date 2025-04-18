import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# Hybrid configuration (works for all environments)
load_dotenv()  # For local development
try:
    # Priority: Streamlit Secrets (for deployment)
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("API key not configured. Check secrets or .env file")
        st.stop()
    
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"API configuration failed: {str(e)}")
    st.stop()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def generate_product_description(prompt):
    """Generate AI description with error handling"""
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"AI generation error: {str(e)}")
        return "Description unavailable"

def display_product_recommendation(refined_df):
    """Main recommendation interface"""
    st.header("Product Recommendation")

    # Filter UI (unchanged from your original)
    category = st.selectbox("Select Category", sorted(refined_df['primary_category'].dropna().unique()))
    max_price = st.slider("Max Price", 
                         min_value=int(refined_df['discounted_price'].min()), 
                         max_value=int(refined_df['discounted_price'].max()), 
                         value=int(refined_df['discounted_price'].mean()))
    gender = st.selectbox("Select Gender", ["Unisex", "Men", "Women"])

    # Filter logic
    filtered_df = refined_df[
        (refined_df['primary_category'] == category) &
        (refined_df['discounted_price'] <= max_price) &
        (refined_df['gender'] == gender)
    ].copy()

    if filtered_df.empty:
        st.warning("No products match your criteria")
        return

    # Display results
    st.subheader("Top Recommendations")
    for _, row in filtered_df.head(5).iterrows():
        col1, col2 = st.columns([1, 3])
        with col1:
            if row['primary_image_link']:
                st.image(row['primary_image_link'], width=150)
        
        with col2:
            st.markdown(f"**{row['product_name']}**")
            st.caption(f"**Brand:** {row['brand']}")
            st.markdown(f"**Price:** ₹{row['discounted_price']} ~~₹{row['retail_price']}~~")
            
            if st.button(f"Generate Description", key=f"desc_{row['pid']}"):
                with st.spinner("Generating AI description..."):
                    prompt = f"Write a 1-2 sentence engaging product description for: {row['product_name']}. Category: {row['primary_category']}, Brand: {row['brand']}. Highlight key features."
                    ai_desc = generate_product_description(prompt)
                    st.success(ai_desc)