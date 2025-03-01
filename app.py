import streamlit as st
st.set_page_config(page_title="ChartBuddyAI", layout="wide")# Expands content to the full screen width

from qdrant_client import QdrantClient
from io import BytesIO
import base64
from src.image_utils import upload_and_display_image, get_image_vector



pages = {
    "Your account": [
        st.Page("search_similar_charts.py", title="Search Similar Charts")
    ],
    "Resources": [
        st.Page("src/ingest.py", title="Ingest New Charts")
    ],
}

pg = st.navigation(pages)
pg.run()







