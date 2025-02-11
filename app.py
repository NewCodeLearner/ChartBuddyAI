from qdrant_client import QdrantClient
from io import BytesIO
import streamlit as st
import base64


# 1. Define the qdrant collection name that we created
collection_name = "stock_charts_images"

# 2. Setup a state variable that we'll re-use throughout the app.
if 'selected_record' not in st.session_state:
    st.session_state.selected_record = None

# 3. Create a function to easily set the "selected_record" value.
def set_selected_record(new_record):
    st.session_state.selected_record = new_record

# This decorator will cache the qdrant client rather than creating new one each time app is refreshed.
@st.cache_resource
def get_client():
    # Uncomment below if using Qdrant managed cloud server to host DB.
#    return QdrantClient(
#        url = st.secrets.get("qdrant_db_url"),
#        api_key = st.secrets.get("qdrant_api_key")
#    )

    # To use the locally setup Qdrant DB using Docker.
    return QdrantClient(host ='localhost',port=6333,prefix="qdrant",timeout=60)