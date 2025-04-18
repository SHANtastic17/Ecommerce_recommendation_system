import streamlit as st
from data_processing import load_data, preprocess_data, display_data_analysis
from recommendation import display_product_recommendation

def main():
    st.title("E-commerce Product Recommendation System")
    st.sidebar.title("Navigation")
    
    # Load dataset (replace with your actual filename)
    dataset_path = "flipkart_com-ecommerce_sample.csv"
    
    try:
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
                try:
                    display_product_recommendation(refined_df)
                except Exception as e:
                    st.error(f"Recommendation error: {str(e)}")
        else:
            st.error("Failed to load dataset")
    except Exception as e:
        st.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()