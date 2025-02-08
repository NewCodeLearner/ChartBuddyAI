#Code file to import documents,images into Qdrant database
from langchain_community.vectorstores import Qdrant
from transformers import ViTImageProcessor, ViTModel
from qdrant_client import QdrantClient
import torch


# 1. Create Qdrant Client

client = QdrantClient(host = 'localhost',port=6333)

#print(client)
#<qdrant_client.qdrant_client.QdrantClient object at 0x000001DDE0B69430>

# 2. Fetch All images in the dataset
import os

base_directory = "img"
all_image_urls = os.listdir(base_directory)
#print(all_image_urls[:5])

#concat image urls with base directory to construct full dir path.
sample_image_urls = all_image_urls
sample_image_urls = list(map(lambda item : f"{base_directory}/{item}",all_image_urls))
print(sample_image_urls[:5])


# 3. Create a dataframe to store the image's metadata
from pandas import DataFrame
from PIL import Image

payloads = DataFrame.from_records({"image_url": sample_image_urls})
payloads["type"] = "stockchart"
print(payloads)
