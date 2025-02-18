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

# Converts an image to an embedding using image model
def get_image_vector(image):
    inputs = processor(images=image,return_tensors="pt")
    outputs = model(**inputs)
    return outputs.logits