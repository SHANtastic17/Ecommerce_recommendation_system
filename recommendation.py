import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

# ===== SECURE API KEY LOADING =====
def get_api_key():
    """Safely retrieves API key with multiple fallback methods"""
    # 1. First try Streamlit Secrets (for deployed apps)
    if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
        return st.secrets['GEMINI_API_KEY']
    
    # 2. Try .env file (for local development)
    load_dotenv()  # Load environment variables
    if os.getenv('GEMINI_API_KEY'):
        return os.getenv('GEMINI_API_KEY')
    
    # 3. Final fallback: Manual input (local dev only)
    if st.sidebar.checkbox("Debug: Enter API Key Manually"):
        manual_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
        if manual_key:
            return manual_key
    
    # If all methods fail
    st.error("""
        API key not found. Please either:
        1. For deployment: Set in Streamlit Secrets
        2. For local dev: Create a .env file
        3. Enter manually above
    """)
    st.stop()

# ===== INITIALIZE GEMINI =====
try:
    genai.configure(api_key=get_api_key())
except Exception as e:
    st.error(f"Failed to configure Gemini: {str(e)}")
    st.stop()

# ===== CACHED AI FUNCTIONS =====
@st.cache_data(ttl=3600)  # Cache for 1 hour
def generate_product_description(prompt):
    """Generates AI description with robust error handling"""
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"AI generation failed: {str(e)}")
        return "Description unavailable - please try again later"

# ===== MAIN RECOMMENDATION UI =====
def display_product_recommendation(refined_df):
    st.header("🔍 Product Recommendation")
    
    with st.container():
        # Filter controls
        col1, col2, col3 = st.columns(3)
        with col1:
            category = st.selectbox(
                "Select Category",
                options=sorted(refined_df['primary_category'].dropna().unique()),
                index=0
            )
        with col2:
            max_price = st.slider(
                "Max Price (₹)",
                min_value=int(refined_df['discounted_price'].min()),
                max_value=int(refined_df['discounted_price'].max()),
                value=int(refined_df['discounted_price'].quantile(0.75))
            )
        with col3:
            gender = st.selectbox("Gender", ["Unisex", "Men", "Women"])

    # Apply filters
    filtered_df = refined_df[
        (refined_df['primary_category'] == category) &
        (refined_df['discounted_price'] <= max_price) &
        (refined_df['gender'] == gender)
    ].copy()

    if filtered_df.empty:
        st.warning("No products match your filters. Try adjusting your criteria.")
        return

    # Display results
    st.subheader(f"Top {min(5, len(filtered_df))} Recommendations")
    for _, row in filtered_df.head(5).iterrows():
        with st.expander(f"✨ {row['product_name']}"):
            col_img, col_text = st.columns([1, 3])
            with col_img:
                if row['primary_image_link']:
                    st.image(row['primary_image_link'], use_column_width=True)
                else:
                    st.warning("No image available")
            
            with col_text:
                st.markdown(f"**Brand:** {row['brand']}")
                st.markdown(f"**Price:** ₹{row['discounted_price']} ~~₹{row['retail_price']}~~")
                st.markdown(f"**Savings:** {int((1 - row['discounted_price']/row['retail_price'])*100)}% off")
                
                if st.button("Generate AI Description", key=f"desc_{row['pid']}"):
                    with st.spinner("🧠 Generating AI-powered description..."):
                        prompt = f"""
                        Create a 2-sentence engaging description for this product:
                        - Name: {row['product_name']}
                        - Category: {row['primary_category']}
                        - Brand: {row['brand']}
                        - Key selling points: {row.get('description', '')[:200]}
                        """
                        st.success(generate_product_description(prompt))