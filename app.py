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

# 4. This decorator will cache the qdrant client rather than creating new one each time app is refreshed.
@st.cache_resource
def get_client():
    # Uncomment below if using Qdrant managed cloud server to host DB.
#    return QdrantClient(
#        url = st.secrets.get("qdrant_db_url"),
#        api_key = st.secrets.get("qdrant_api_key")
#    )

    # To use the locally setup Qdrant DB using Docker.
    return QdrantClient(host ='localhost',port=6333,prefix="qdrant",timeout=60)

# 5. When the app first starts, lets show the user sample images.
def get_initial_records():
    client = get_client()

    records, _ = client.scroll(
        collection_name = collection_name,
        with_vectors = False,
        limit = 12
    )
    return records

# 6. This function will be called , If the user selected a record for which they want to see similar items.
def get_similar_records():
    client = get_client()

    if st.session_state.selected_record is not None:
        return client.recommend(
        collection_name = collection_name,
        positive =  [st.session_state.selected_record.id],
        limit =12
    )


