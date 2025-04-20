import streamlit as st
import io
import base64
import random,os
from PIL import Image
import torch


st.write("App started")

@st.cache_resource
def load_clip_model():
    from transformers import CLIPModel, CLIPProcessor
    model = CLIPModel.from_pretrained(model_path)
    processor = CLIPProcessor.from_pretrained(model_path)
    return model,processor
    #commented direct import from Huggingface
    #return CLIPModel.from_pretrained("openai/clip-vit-base-patch32"), CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


model_path = os.getenv('MODEL_PATH')  # Adjust if relative path changes
print('Search similar charts - before clip model load')

def get_image_vector(image):
    model, processor = load_clip_model()  # Load only when required
    inputs = processor(images=image,return_tensors="pt")
    with torch.no_grad():
        image_features = model.get_image_features(**inputs)  # Get embeddings
    return image_features.cpu().numpy().flatten().tolist()  # Convert to list of floats


@st.cache_resource
def get_client():
    from qdrant_client import QdrantClient
    # Uncomment below if using Qdrant managed cloud server to host DB.
#    return QdrantClient(
#        url = st.secrets.get("qdrant_db_url"),
#        api_key = st.secrets.get("qdrant_api_key")
#    )

    # To use the locally setup Qdrant DB using Docker.
    return QdrantClient(host ='localhost',port=6333,prefix="qdrant",timeout=60)


def upload_and_display_image():
    client = get_client()  # Load Qdrant client only when needed
    uploaded_file = st.file_uploader("Upload a chart image", type=["png","jpg","jpeg"])

    if uploaded_file:
        uploaded_image = Image.open(uploaded_file).convert("RGB")
        st.image(uploaded_image,caption="Uploaded Image",use_container_width=True)

        # Store uploaded image in session state
        if "uploaded_image" not in st.session_state:
            st.session_state.uploaded_image = uploaded_image

        if st.button("🔍 Show Similar Charts", key="search_uploaded"):
            with st.spinner("Searching for similar charts..."):
              # Ensure image vector is generated only once
                st.session_state.uploaded_image_vector = get_image_vector(uploaded_image)

            # Search Qdrant for similar images
            search_results = client.search(
                collection_name=collection_name,
                query_vector=st.session_state.uploaded_image_vector,
                limit=5
            )

            # Store results in session state to persist across reruns
            st.session_state.uploaded_search_results = search_results

    # ----------------- DISPLAY SEARCH RESULTS -----------------
    if "uploaded_search_results" in st.session_state:
        st.subheader("🔍 Similar Chart Images")
        cols = st.columns(3)

        for idx, result in enumerate(st.session_state.uploaded_search_results):
            col_idx = idx % 3
            # Retrieve image from DB
            image_bytes_str = result.payload["base64"]  

            # Decode the base64 string into bytes , Image.open() expects a byte object 
            image_bytes = base64.b64decode(image_bytes_str)
            
            # Convert back to image
            image = Image.open(io.BytesIO(image_bytes))  
            with cols[col_idx]:
                st.image(image, caption=f"Match {idx+1}", use_container_width=True)
    return None


# 1. Define the qdrant collection name that we created
collection_name = os.getenv('COLLECTION_NAME')


# Upload image and display it
image = upload_and_display_image()

# 2. Setup a state variable that we'll re-use throughout the app.
if 'selected_record' not in st.session_state:
    st.session_state.selected_record = None

# 3. Create a function to easily set the "selected_record" value.
def set_selected_record(new_record):
    st.session_state.selected_record = new_record
    # Also store the image bytes so the chat page can display the selected chart.
    st.session_state.selected_chart_image = get_bytes_from_base64(new_record.payload["base64"])


# 5. When the app first starts, lets show the user sample images.
def get_initial_records():
    client = get_client()

    all_records, _ = client.scroll(
        collection_name = collection_name,
        with_vectors = True,
        limit = 10000
    )

    # Sample 99 random records (if available)
    if len(all_records) > 99:
        records = random.sample(all_records, 99)
    else:
        records = all_records

    return records


# 6. This function will be called , If the user selected a record for which they want to see similar items.

# Retrieve the Embedding for the Selected Record
def get_vector_by_id(client, collection_name, record_id):

    response = client.retrieve(
        collection_name=collection_name,
        ids=[record_id],  # Use retrieve instead of scroll,
        with_vectors = True
    )

    if response[0]:  # Ensure data is found
        return response[0].vector
    return None

def get_similar_records():
    client = get_client()

   
    # Use query_points for Search
    if st.session_state.selected_record is not None:
        record_id = st.session_state.selected_record.id
        print(f"Searching for similar charts to record ID: {record_id}")  

        vector = get_vector_by_id(client, collection_name, record_id)

        if vector:
            results = client.query_points(
                collection_name=collection_name,
                query=vector,  # Use the extracted vector,
                with_payload=True,
                limit=13
            )
            return results.points
        else:
            st.warning("Vector not found for selected record.")


# 7. Define a convenience function to convert base64 back into bytes
#    that can be used by Steamlit to render images.
def get_bytes_from_base64(base64_string):
    return io.BytesIO(base64.b64decode(base64_string))

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

# Save the ID of the base search image for filtering
# Only set base_id if a selected_record exists
base_record = st.session_state.get("selected_record")
base_id = base_record.id if base_record is not None else None


for idx, record in enumerate(records):
    col_idx = idx % 3
    image_bytes = get_bytes_from_base64(record.payload['base64'])

    # Skip the base image if its id matches the query image id
    # If a base image is selected and its ID matches the current record, skip it.
    if base_id is not None and record.id == base_id:
        continue
    
    with column[col_idx]:
        st.image(
            image = image_bytes,
            use_container_width=True
        )
        
        # Only display the similarity score if it exists (e.g., after a similarity search)
        if hasattr(record, 'score') and record.score is not None:
            st.write(f"Similarity: {record.score:.3f}")

        st.button(
            label = "Find similar charts",
            key = record.id,
            on_click = set_selected_record, # call set the selected fn 
            args = [record]
        )    

