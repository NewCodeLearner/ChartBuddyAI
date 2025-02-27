import streamlit as st
st.set_page_config(page_title="ChartBuddyAI", layout="wide")# Expands content to the full screen width

from qdrant_client import QdrantClient
from io import BytesIO
import base64
from src.image_utils import upload_and_display_image, get_image_vector


# 1. Define the qdrant collection name that we created
collection_name = "stock_charts_images_clip"


# Upload image and display it
image = upload_and_display_image()

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
        limit = 99
    )
    return records

# 6. This function will be called , If the user selected a record for which they want to see similar items.

# Retrieve the Embedding for the Selected Record
def get_vector_by_id(client, collection_name, record_id):

    response = client.scroll(
        collection_name=collection_name,
        scroll_filter={"must": [{"key": "id", "match": {"value": record_id}}]},
        limit=1
    )

    print(response)
    if response[0]:  # Ensure data is found
        return response[0][0].vector
    return None

def get_similar_records():
    client = get_client()

    #Commenting the recommend API to use query_points API
    #if st.session_state.selected_record is not None:
    #    return client.recommend(
    #    collection_name = collection_name,
    #    positive =  [st.session_state.selected_record.id],
    #    limit =12
    #)
    
    # Use query_points for Search
    if st.session_state.selected_record is not None:
        record_id = st.session_state.selected_record.id
        print(f"Searching for similar charts to record ID: {record_id}")  

        vector = get_vector_by_id(client, collection_name, record_id)
        print(vector)

        if vector:
            results = client.query_points(
                collection_name=collection_name,
                query_vector=vector,  # Use the extracted vector
                limit=12
            )
            return results
        else:
            st.warning("Vector not found for selected record.")


# 7. Define a convenience function to convert base64 back into bytes
#    that can be used by Steamlit to render images.
def get_bytes_from_base64(base64_string):
    return BytesIO(base64.b64decode(base64_string))

# 8. Get the records. This function will be re-called multiple times 
#    throughout the lifecycle of our app. We fetch the original record
#    if there is nothing selected- otherwise fetch recommendations.
records = get_similar_records(
) if st.session_state.selected_record is not None else get_initial_records()

# 9. If we have a selected record, then show that image at the top of the screen
if st.session_state.selected_record:
    image_bytes = get_bytes_from_base64(
        st.session_state.selected_record.payload["base64"]
    )
    st.header("Stock Charts Similar to:")
    st.image(
        image= image_bytes
    )
    st.divider()

# 10. Setup the grid to render images.
column = st.columns(3)

# 11. Iterate over all the fetched records from DB
#     and render a preview of each image using base64 string.


for idx, record in enumerate(records):
    col_idx = idx % 3
    image_bytes = get_bytes_from_base64(record.payload['base64'])
    #print(image_bytes)
    with column[col_idx]:
        st.image(
            image = image_bytes,
            use_container_width=True
        )

        st.button(
            label = "Find similar charts",
            key = record.id,
            on_click = set_selected_record, # call set the selected fn 
            args = [record]
        )    





