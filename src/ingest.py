#Code file to import documents,images into Qdrant database
from langchain_community.vectorstores import Qdrant
from transformers import ViTImageProcessor, ViTModel
from qdrant_client import QdrantClient
import torch


# Create Qdrant Client

client = QdrantClient(host = 'localhost',port=6333)

print(client)
