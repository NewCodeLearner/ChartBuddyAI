import os
#from transformers import AutoImageProcessor, ResNetForImageClassification
from PIL import Image,ImageEnhance
import base64
import streamlit as st
import io,time
from qdrant_client import QdrantClient , models
import torch
from transformers import CLIPModel, CLIPProcessor

# Load environment variables from the .env file (if present)

collection_name = os.getenv('COLLECTION_NAME')

# Import the model and tokenizer then run 
# all the images through it to create the embeddings.
#from transformers import AutoImageProcessor, ResNetForImageClassification

#commenting resnet model to use CLIP model
#processor = AutoImageProcessor.from_pretrained("microsoft/resnet-50")
#model = ResNetForImageClassification.from_pretrained("microsoft/resnet-50")

#Use Streamlit caching so it doesn’t reload the model every time:
@st.cache_resource
def load_clip_model():
    return CLIPModel.from_pretrained("openai/clip-vit-base-patch32"), CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Lazy Initialization
model, processor, client = None, None, None

print('before clip model load')
#model, processor = load_clip_model()

def get_clip_model():
    global model, processor
    if model is None or processor is None:
        model, processor = load_clip_model()
    return model, processor

client = QdrantClient(host='localhost', port=6333, prefix="qdrant", timeout=60)


def set_selected_record(new_record):
    st.session_state.selected_record = new_record

# Converts an image to an embedding using image model
#def get_image_vector(image):
#    inputs = processor(images=image,return_tensors="pt")
#    outputs = model(**inputs)
#    return outputs.logits

def get_image_vector(image):
    model, processor = get_clip_model()  # Load only when required
    inputs = processor(images=image,return_tensors="pt")
    with torch.no_grad():
        image_features = model.get_image_features(**inputs)  # Get embeddings
    return image_features.cpu().numpy().flatten().tolist()  # Convert to list of floats


# Enhance the image using PIL.ImageEnhance
def enhance_image(pil_image, upscale_factor=2, sharpness_factor=2.0, contrast_factor=1.5, color_factor=1.2):
    # Upscale the image using a high-quality interpolation (BICUBIC)
    new_size = (pil_image.width * upscale_factor, pil_image.height * upscale_factor)
    upscaled_image = pil_image.resize(new_size, Image.BICUBIC)

    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(upscaled_image)
    sharp_image = enhancer.enhance(sharpness_factor)
    
    # Enhance contrast
    contrast_enhancer = ImageEnhance.Contrast(sharp_image)
    contrast_image = contrast_enhancer.enhance(contrast_factor)
    
    # Enhance color saturation
    color_enhancer = ImageEnhance.Color(contrast_image)
    final_image = color_enhancer.enhance(color_factor)
    
    return final_image
    

# Streamlit component for uploading and displaying an image.
def upload_and_display_image():

    #client = get_qdrant_client()  # Load Qdrant client only when needed
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

def ingest_chart_image():
    
    #client = get_qdrant_client()  # Load Qdrant client only when needed

    # Wrap the stored image bytes into a BytesIO object
    if 'downloaded_chart_image' in st.session_state:
        img_buffer = io.BytesIO(st.session_state.downloaded_chart_image)

    # Get the vector embedding from the image using your CLIP or similar model.
    # Convert BytesIO to PIL Image
    pil_image = Image.open(img_buffer)
    vector = get_image_vector(pil_image)

    # Reset the file pointer again to read for base64 conversion
    img_buffer.seek(0)
    image_bytes = img_buffer.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

    # Prepare payload with any metadata you want (for example, the base64 string, timestamp, etc.)
    payload = {
        "base64": base64_image,
        "type": "Moneycontrol",
        "image_url": None
    }
    # Use a unique id; here we simply use a timestamp or you can integrate your own id generation logic.
    record_id = int(time.time())

    # Create a Qdrant PointStruct with id, vector, and payload
    point = models.PointStruct(
        id=record_id,
        vector=vector,   # Make sure this is a list of floats (e.g., 512 dims)
        payload=payload
    )
    
    # Upsert the point into the Qdrant collection
    client.upsert(
        collection_name=collection_name,
        points=[point]
    )

