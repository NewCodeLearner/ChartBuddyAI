import streamlit as st
import torch
from transformers import CLIPModel, CLIPProcessor

@st.cache_resource
def load_clip_model():
    return CLIPModel.from_pretrained("openai/clip-vit-base-patch32"), CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Lazy Initialization
model, processor, client = None, None, None

print('before clip model load')
model, processor = load_clip_model()

def get_image_vector(image):
    #model, processor = get_clip_model()  # Load only when required
    inputs = processor(images=image,return_tensors="pt")
    with torch.no_grad():
        image_features = model.get_image_features(**inputs)  # Get embeddings
    return image_features.cpu().numpy().flatten().tolist()  # Convert to list of floats