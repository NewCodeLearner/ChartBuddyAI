import streamlit as st
import base64
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
    return None

    # For demonstration, return hard-coded values:
    scid = "ICI02"
    #exchange_id = "ICICIBANK"
    return scid, exchange_id

st.title("Agent for Fetching New Stock Charts")

user_input = st.text_input("Enter your command (e.g., 'Show me the chart for ICICIBANK'):")