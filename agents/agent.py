import streamlit as st
import base64
import os
from dotenv import load_dotenv
from groq import Groq
from src.image_utils import upload_and_display_image, get_image_vector
from fetch_chart_agent import fetch_chart_image  # Import your function

# Tool to extract stock information from the user prompt.
def get_stock_name(prompt):
    """
    Extracts stock-related parameters from the user prompt.
    For now, returns dummy values. You can replace this logic with NLP extraction.
    """
    # For demonstration, return hard-coded values:
    scid = "ICI02"
    exchange_id = "ICICIBANK"
    return scid, exchange_id

st.title("Agent for Fetching New Stock Charts")