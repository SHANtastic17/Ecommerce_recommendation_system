
# 🛍️ E-commerce Product Recommendation System Powered by Gemini AI

This is a personalized e-commerce product recommendation system that leverages **Google Gemini (GenAI)** to deliver intelligent product suggestions and generate **AI-powered product descriptions** on demand. Built using **Streamlit**, **SQLite**, and **Pandas**, it provides a smooth and modern UI for users to explore, filter, and understand product offerings.

## 🚀 Features

- **AI-Powered Descriptions:** Generates compelling product summaries using the Gemini 2.0 Flash model.
- **Smart Filtering:** Users can filter products by category, gender, and max price.
- **Interactive Recommendations:** Shows the top 5 matching products with visuals and discounts.
- **Data Analysis Dashboard:** Visualizes price and discount distributions using Seaborn & Matplotlib.
- **SQLite Backend:** Products are loaded from a local `ecommerce.db` database.
- **API Fallback:** Dual-mode Gemini API integration (SDK + HTTP fallback) ensures reliability.

## 📁 Project Structure

```
ecommerce-product-recommendation/
├── app.py                      # Main Streamlit app with navigation
├── data_processing.py          # Handles SQLite data access and visualizations
├── recommendation.py           # Core logic for AI product suggestions and Gemini integration
├── database/ecommerce.db       # SQLite database (you must provide this)
├── requirements.txt            # Python dependencies
└── README.md                   # Project overview and instructions
```

## 🛠️ Setup Instructions

1. **Clone the Repository**

```bash
git clone https://github.com/your-username/ecommerce_recommendation_system.git
cd ecommerce-product-recommendation-genai
```

2. **Install Dependencies**

```bash
pip install -r requirements.txt
```

3. **Set Up Gemini API Key**

- Option 1: Create a `.streamlit/secrets.toml` file:

```toml
GEMINI_API_KEY = "your-gemini-api-key"
```

- Option 2: Set it as an environment variable:

```bash
export GEMINI_API_KEY=your-gemini-api-key
```

- Option 3: Input manually in the app if key is not found.

4. **Add the Database**

Make sure you have `ecommerce.db` inside the `database/` directory with a `products` table.

## ▶️ Run the App

```bash
streamlit run app.py
```

## 📊 Dataset

This project uses a **Flipkart-inspired product dataset** stored in an SQLite database. It includes:

- Product ID, Name, Brand
- Retail & Discounted Price
- Image Links, Descriptions
- Category and Gender fields

## 💡 Future Enhancements

- Add user login & preferences tracking
- Use vector search (e.g., FAISS) for semantic retrieval
- Add review-based sentiment filtering
- Integrate actual e-commerce APIs
- Switch between multiple LLMs via dropdown

## 📄 License

MIT License — Feel free to use, modify, and share!
