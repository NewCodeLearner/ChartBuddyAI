import streamlit as st
import base64
from PIL import Image
import requests
import re,io
from dotenv import load_dotenv
from src.image_utils import ingest_chart_image,enhance_image
from agents.fetch_chart_agent import fetch_chart_image  # Import your function
from src.ingest import ingest_all_charts
from agents.get_stock_name_agent import get_stock_name
import json


st.title("Ingest New Stock Charts")

# Create tabs for the two functionalities
tab1, tab2 = st.tabs(["Fetch Chart", "Ingest All Charts"])

with tab1:
    st.header("Agent for Fetching New Stock Charts")
    user_input = st.text_input("Enter your command (e.g., 'Show me the chart for ICICIBANK'):")

    if st.button("Run Agent - Fetch Chart"):
        #result = get_stock_name(user_input)
        response = get_stock_name(user_input)
        print(type(response))
        print(response)
        exchange_id = json.loads(response)
        print('exchange_id ' , exchange_id)
        exchange_id = exchange_id['symbol']  #Response :  {'action': 'show chart', 'symbol': 'CENTRALBK'}

        result = fetch_chart_image(exchange_id)
        image_bytes = base64.b64decode(result)
        downloaded_image = Image.open(io.BytesIO(image_bytes))
        # Enhance the image
        enhanced_image = enhance_image(downloaded_image)
        if 'downloaded_chart_image' not in st.session_state:
            #Pass the Enhanced image bytes to storage instead of downloaded basic image
            buffer = io.BytesIO()
            enhanced_image.save(buffer, format="PNG")  # or "JPEG" depending on your needs
            buffer.seek(0)
            enhanced_image_bytes = buffer.getvalue()
            st.session_state.downloaded_chart_image = enhanced_image_bytes

        st.image(enhanced_image,caption= f"Downloaded Stock Chart Image for {exchange_id} ")
        st.write(f"Downloaded Stock Chart Image for {exchange_id} ")


    if st.button("Save Chart Image"):
        ingest_chart_image()
        st.write(f"Ingested chart image into Qdrant.")

with tab2:
    st.header("Ingest All Charts")
    if st.button("Ingest All Charts"):
        response = ingest_all_charts()  # This function ingests the chart stored in img folder locally