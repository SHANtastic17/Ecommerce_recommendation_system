import os
import streamlit as st
from google import genai
import requests
from datetime import datetime

# Initialize session state for caching
if 'ai_descriptions' not in st.session_state:
    st.session_state.ai_descriptions = {}
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False

def initialize_gemini_client():
    """Initialize Gemini client with multiple key sources"""
    api_key = (
        st.secrets.get("GEMINI_API_KEY") or
        os.getenv("GEMINI_API_KEY") or
        st.session_state.get("manual_api_key")
    )
    
    if not api_key:
        st.error("🔑 No API key found in secrets, environment variables, or session state")
        return None
    
    try:
        client = genai.Client(api_key=api_key)
        
        # Quick test to validate connection
        test_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[{"parts": [{"text": "Test connection"}]}]
        )
        
        st.session_state.api_key_valid = True
        return client
    except Exception as e:
        st.error(f"🔌 Connection failed: {str(e)}")
        st.session_state.api_key_valid = False
        return None

def generate_with_sdk(client, prompt):
    """Generate content using official SDK"""
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[{"parts": [{"text": prompt}]}],
            
        )
        return response.text
    except Exception as e:
        st.error(f"🤖 SDK generation failed: {str(e)}")
        return None

def generate_with_http(prompt):
    """Fallback HTTP API call"""
    try:
        api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent",
            params={"key": api_key},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.7,
                    "topP": 0.9,
                    "maxOutputTokens": 150
                }
            },
            timeout=10
        )
        if response.status_code == 200:
            return response.json()['candidates'][0]['content']['parts'][0]['text']
        return None
    except Exception as e:
        st.error(f"🌐 HTTP fallback failed: {str(e)}")
        return None

def generate_product_description(prompt, product_id):
    """Main generation function with caching and fallbacks"""
    # Return cached description if available
    if product_id in st.session_state.ai_descriptions:
        return st.session_state.ai_descriptions[product_id]
    
    # Initialize client if not done
    if 'gemini_client' not in st.session_state:
        st.session_state.gemini_client = initialize_gemini_client()
    
    # Attempt SDK generation first
    if st.session_state.gemini_client:
        result = generate_with_sdk(st.session_state.gemini_client, prompt)
        if result:
            st.session_state.ai_descriptions[product_id] = result
            return result
    
    # Fallback to HTTP API
    result = generate_with_http(prompt)
    if result:
        st.session_state.ai_descriptions[product_id] = result
        return result
    
    return "⚠️ All generation attempts failed. Please check your API key."

def display_product_recommendation(refined_df):
    st.header("Smart Product Recommendations")
    st.caption(f"Powered by Gemini 2.0 Flash | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    # API Key Fallback Input
    if not (st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")):
        st.session_state.manual_api_key = st.text_input(
            "Enter Gemini API Key",
            type="password",
            help="Get your key from https://aistudio.google.com/app/apikey"
        )
    
    # Filter Controls
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox(
                "Product Category",
                options=sorted(refined_df['primary_category'].dropna().unique()),
                index=0
            )
            gender = st.radio(
                "Gender",
                options=["All", "Men", "Women", "Unisex"],
                horizontal=True
            )
        with col2:
            max_price = st.slider(
                "Maximum Price (₹)",
                min_value=int(refined_df['discounted_price'].min()),
                max_value=int(refined_df['discounted_price'].max()),
                value=int(refined_df['discounted_price'].median())
            )
    
    # Apply Filters
    filtered_df = refined_df[
        (refined_df['primary_category'] == category) &
        (refined_df['discounted_price'] <= max_price)
    ]
    if gender != "All":
        filtered_df = filtered_df[filtered_df['gender'] == gender]
    
    # Display Results
    if filtered_df.empty:
        st.warning("No products match your selected filters")
        return
    
    st.subheader(f"Top {min(5, len(filtered_df))} Recommendations")
    for idx, (_, row) in enumerate(filtered_df.head(5).iterrows()):
        with st.container(border=True):
            cols = st.columns([1, 3])
            with cols[0]:
                st.image(
                    row['primary_image_link'] or "https://via.placeholder.com/150",
                    width=200,
                    caption=row['brand']
                )
            with cols[1]:
                st.markdown(f"#### {row['product_name']}")
                st.markdown(f"**Brand:** {row['brand']}")
                st.markdown(f"**Price:** ₹{row['discounted_price']:,} ~~₹{row['retail_price']:,}~~")
                st.markdown(f"**Discount:** {int((1-row['discounted_price']/row['retail_price'])*100)}% off")
                
                if st.button(
                    "✨ Generate AI Description",
                    key=f"desc_{row['pid']}",
                    type="secondary",
                    use_container_width=True
                ):
                    with st.spinner("Generating professional description..."):
                        prompt = f"""Create a compelling 2-3 sentence product description for an e-commerce site:
                        
                        **Product:** {row['product_name']}
                        **Category:** {row['primary_category']}
                        **Brand:** {row['brand']}
                        **Key Selling Points:**
                        - Discounted from ₹{row['retail_price']} to ₹{row['discounted_price']}
                        - {row['description'][:100]}...
                        
                        Make it engaging and highlight the value proposition."""
                        
                        description = generate_product_description(prompt, row['pid'])
                        st.success(description)