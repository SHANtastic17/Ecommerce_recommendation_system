import streamlit as st
from PIL import Image
import requests
from io import BytesIO
from google import generativeai as genai

# Configure Gemini API
 # Replace with your real API key

def generate_recommendation(prompt):
    """
    Generate product recommendation using Gemini AI.
    
    Args:
        prompt (str): Prompt to send to Gemini.
    
    Returns:
        str: Gemini's response.
    """
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def display_product_recommendation(refined_df):
    """
    Streamlit UI for taking user input and displaying recommendations.
    
    Args:
        refined_df (pd.DataFrame): Preprocessed dataset DataFrame.
    """
    st.header("Product Recommendation")

    # User input
    category = st.selectbox("Select a category", refined_df['primary_category'].unique())
    gender = st.selectbox("Select gender preference", ["Unisex", "Men", "Women"])
    max_price = st.slider("Select maximum price", 100, 10000, 1000)

    if st.button("Recommend"):
        # Create prompt for Gemini
        prompt = (
            f"Suggest a Flipkart product under ₹{max_price} in the '{category}' category for {gender.lower()} consumers. "
            f"Only recommend products available in the dataset. Keep the recommendation short and relevant."
        )

        # Generate recommendation
        recommendation_text = generate_recommendation(prompt)
        st.subheader("Gemini's Recommendation")
        st.write(recommendation_text)

        # Optional: Display a matching product from dataset
        match = refined_df[
            (refined_df['primary_category'] == category) &
            (refined_df['gender'].str.lower() == gender.lower()) &
            (refined_df['discounted_price'] <= max_price)
        ].sample(n=1)

        if not match.empty:
            product = match.iloc[0]
            st.markdown(f"**Product Name**: {product['product_name']}")
            st.markdown(f"**Price**: ₹{product['discounted_price']} (Retail: ₹{product['retail_price']})")
            st.markdown(f"**Brand**: {product['brand']}")
            st.markdown(f"**Description**: {product['description']}")
            st.markdown(f"[Product Link]({product['product_url']})")

            if product['primary_image_link']:
                try:
                    response = requests.get(product['primary_image_link'])
                    img = Image.open(BytesIO(response.content))
                    st.image(img, caption="Product Image", use_column_width=True)
                except:
                    st.warning("Unable to load product image.")
