import streamlit as st
from data_processing import load_data, preprocess_data, display_data_analysis
from recommendation import display_product_recommendation
import os
from datetime import datetime

# Configure page settings
st.set_page_config(
    page_title="E-Commerce Recommendation System",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=3600, show_spinner=True)
def load_and_process_data():
    """Load and preprocess data with caching and error handling"""
    dataset_path = "flipkart_com-ecommerce_sample.csv"
    try:
        with st.spinner("🧠 Loading and preprocessing data..."):
            df = load_data(dataset_path)
            if df is not None:
                return preprocess_data(df)
        return None
    except Exception as e:
        st.error(f"❌ Data loading failed: {str(e)}")
        return None

def main():
    # Sidebar navigation
    with st.sidebar:
        st.title("🔍 Navigation")
        app_mode = st.radio(
            "Select Mode",
            ["📊 Data Analysis", "🛒 Product Recommendations"],
            index=1
        )
        
        st.divider()

    # Main content
    st.title("🛍️ E-Commerce Recommendation System")
    st.caption("Powered by Gemini 2.0 Flash | Real-time personalized recommendations")
    
    # Load data
    refined_df = load_and_process_data()
    if refined_df is None:
        st.error("Failed to load dataset. Please check the file path.")
        return

    # Route to selected mode
    if "Data Analysis" in app_mode:
        display_data_analysis(refined_df)
    else:
        display_product_recommendation(refined_df)

if __name__ == "__main__":
    main()