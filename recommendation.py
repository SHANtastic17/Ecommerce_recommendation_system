import os
import streamlit as st
import google.generativeai as genai
from google.api_core import retry
from datetime import datetime

# --- Configuration ---
def configure_genai():
    """Configure Gemini API with multiple fallback options"""
    try:
        # Try getting API key from multiple sources
        api_key = (
            os.getenv("GEMINI_API_KEY") or 
            st.secrets.get("GEMINI_API_KEY") or
            st.session_state.get("GEMINI_API_KEY")
        )
        
        if not api_key:
            st.error("🔑 No Gemini API key found in environment or secrets")
            return False

        # Configure with multiple endpoint options
        genai.configure(
            api_key=api_key,
            transport="rest",
            client_options={
                'api_endpoint': 'https://generativelanguage.googleapis.com/v1'
            }
        )

        # Verify connection with retry logic
        @retry.Retry()
        def verify_connection():
            try:
                models = genai.list_models()
                if not any(m.name.startswith('models/gemini') for m in models):
                    raise ValueError("No Gemini models available")
                return True
            except Exception as e:
                st.error(f"🔌 Connection failed: {str(e)}")
                return False

        return verify_connection()
        
    except Exception as e:
        st.error(f"⚙️ Configuration error: {str(e)}")
        return False

# --- AI Generation ---
def generate_product_description(prompt, product_id):
    """Generate description with caching and fallback logic"""
    # Initialize session cache if not exists
    if 'descriptions_cache' not in st.session_state:
        st.session_state.descriptions_cache = {}
    
    # Return cached description if available
    if product_id in st.session_state.descriptions_cache:
        return st.session_state.descriptions_cache[product_id]
    
    if not configure_genai():
        return "⚠️ API configuration failed"

    try:
        # Try multiple model versions
        for model_name in ["gemini-1.0-pro", "gemini-pro"]:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_output_tokens": 150
                    }
                )
                if response.text:
                    # Cache successful responses
                    st.session_state.descriptions_cache[product_id] = response.text
                    return response.text
            except Exception:
                continue
                
        return "⚠️ Could not generate description"
    except Exception as e:
        st.error(f"🤖 Generation error: {str(e)}")
        return "⚠️ Description generation failed"

# --- Recommendation UI ---
def display_product_recommendation(refined_df):
    st.header("🛒 Product Recommendations")
    
    # Filter controls
    col1, col2 = st.columns([2, 1])
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
    
    gender = st.radio(
        "Gender",
        options=["All", "Men", "Women", "Unisex"],
        horizontal=True
    )

    # Apply filters
    filtered_df = refined_df[
        (refined_df['primary_category'] == category) &
        (refined_df['discounted_price'] <= max_price)
    ]
    if gender != "All":
        filtered_df = filtered_df[filtered_df['gender'] == gender]
    
    # Display results
    if filtered_df.empty:
        st.warning("No products match your criteria")
        return
        
    st.subheader(f"🔍 Top {min(5, len(filtered_df))} Recommendations")
    for _, row in filtered_df.head(5).iterrows():
        with st.expander(f"**{row['product_name']}**", expanded=True):
            col_img, col_info = st.columns([1, 3])
            
            with col_img:
                st.image(
                    row['primary_image_link'] or "https://via.placeholder.com/150",
                    width=150
                )
            
            with col_info:
                st.markdown(f"**Brand:** {row['brand']}")
                st.markdown(f"**Price:** ₹{row['discounted_price']:,} ~~₹{row['retail_price']:,}~~")
                st.markdown(f"**Discount:** {int((1-row['discounted_price']/row['retail_price'])*100)}% off")
                
                if st.button(
                    "Generate AI Description",
                    key=f"desc_{row['pid']}",
                    type="secondary"
                ):
                    prompt = f"""Write a compelling 2-3 sentence product description for:
                    - Name: {row['product_name']}
                    - Category: {row['primary_category']}
                    - Brand: {row['brand']}
                    - Discounted Price: ₹{row['discounted_price']}
                    - Original Price: ₹{row['retail_price']}
                    """
                    with st.spinner("Generating description..."):
                        description = generate_product_description(prompt, row['pid'])
                        st.success(description)