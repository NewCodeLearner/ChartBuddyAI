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
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image,caption="Uploaded Image",use_container_width=True)
        st.button(

            label = "Find similar charts",
            key = id,
            on_click = set_selected_record, # call set the selected fn 
            args = [image]
        ) 
        return image
    
    return None