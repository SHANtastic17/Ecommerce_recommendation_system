import streamlit as st
from data_processing import preprocess_data, display_data_analysis
from recommendation import display_product_recommendation

# Initialize session state variables
if 'ai_descriptions' not in st.session_state:
    st.session_state.ai_descriptions = {}
if 'api_key_valid' not in st.session_state:
    st.session_state.api_key_valid = False
if 'gemini_client' not in st.session_state:
    st.session_state.gemini_client = None

# Configure page settings
st.set_page_config(
    page_title="E-Commerce Product Recommendation System",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=3600)
def load_and_process_data():
    """Load and preprocess data with caching"""
    return preprocess_data()

def main():
    # Sidebar navigation
    with st.sidebar:
        st.title("🔍 Navigation")
        app_mode = st.radio(
            "Select Mode",
            ["📊 Data Analysis", "🛒 Product Recommendations"],
            index=1
        )
    
    # Main content
    st.title("🛍️ E-Commerce Product Recommendation System")
    
    # Load data
    refined_df = load_and_process_data()
    
    # Route to selected mode
    if "Data Analysis" in app_mode:
        display_data_analysis(refined_df)
    else:
        display_product_recommendation(refined_df)

if __name__ == "__main__":
    main()