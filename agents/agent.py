import streamlit as st
import base64
import requests
import os,re
from dotenv import load_dotenv
from groq import Groq
from src.image_utils import upload_and_display_image, get_image_vector
from agents.fetch_chart_agent import fetch_chart_image  # Import your function

# Tool to extract stock information from the user prompt.
def get_stock_name(prompt):
    """
    Extracts stock-related parameters from the user prompt.
    For now, returns dummy values. You can replace this logic with NLP extraction.
    """

    # Regular expression to capture a word following 'for'
    pattern = re.compile(r'\bfor\s+([A-Z0-9]+)\b', re.IGNORECASE)
    match = pattern.search(prompt)
    if match:
        # Return the captured group as uppercase
        exchange_id = match.group(1).upper()
    else:
        # Fallback: try to take the last token if it's all uppercase and numeric
        tokens = prompt.strip().split()
        if tokens and tokens[-1].isupper():
            exchange_id = tokens[-1]
    print (exchange_id)

    query = exchange_id
    # Construct the API URL by inserting the query text.
    url = f"https://priceapi.moneycontrol.com/techCharts/indianMarket/stock/search?limit=30&query={query}&type=&exchange="

    try:
        #Add Request Headers:The endpoint might be blocking requests that don't mimic a browser.
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Referer": "https://www.moneycontrol.com/",
                  }
        response = requests.get(url,headers=headers)
        response.raise_for_status()
        data = response.json()
        print(data)

        # The API might return a list of results. Adjust the key(s) based on the actual structure.
        stocks = data
        if stocks:
            # We'll choose the first stock in the result as the match.
            stock = stocks[0]
            # Adjust these keys based on the API response; here we assume keys "scId" and "exchangeId" or similar.
            scid = stock.get("symbol") or stock.get("symbol")
            exchange_id = stock.get("ticker") or stock.get("ticker")
            return scid, exchange_id

    except Exception as e:
        print(f"Error in get_stock_name : {e}")
    
    
    # For demonstration, return hard-coded values:
    scid = "DUMMY01"
    exchange_id = "DUMMY01"
    return scid, exchange_id

st.title("Agent for Fetching New Stock Charts")

user_input = st.text_input("Enter your command (e.g., 'Show me the chart for ICICIBANK'):")

if st.button("Run Agent"):
    result = get_stock_name(user_input)
    st.write(result)