import torch
from transformers import AutoImageProcessor, ResNetForImageClassification
from PIL import Image
import streamlit as st
import io

# Import the model and tokenizer then run 
# all the images through it to create the embeddings.
from transformers import AutoImageProcessor, ResNetForImageClassification

processor = AutoImageProcessor.from_pretrained("microsoft/resnet-50")
model = ResNetForImageClassification.from_pretrained("microsoft/resnet-50")


def set_selected_record(new_record):
    st.session_state.selected_record = new_record

# Converts an image to an embedding using image model
def get_image_vector(image):
    inputs = processor(images=image,return_tensors="pt")
    outputs = model(**inputs)
    return outputs.logits

# Streamlit component for uploading and displaying an image.
def upload_and_display_image():
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
    
    return None