#Code file to import documents,images into Qdrant database
from langchain_community.vectorstores import Qdrant
from transformers import ViTImageProcessor, ViTModel
from qdrant_client import QdrantClient
import torch


# 1. Create Qdrant Client

qclient = QdrantClient(host ='localhost',port=6333,prefix="qdrant",timeout=60)

print(qclient.info())
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
#print(payloads)

# 4. Create PIL (Python Imaging Library) image from each of the local URLs.
# PIL provides a wide range of functions for image processing, such as resizing, cropping, rotating, and applying filters.
images =  list(map(lambda imgurl : Image.open(imgurl),payloads['image_url']))
#print(images)



# 5. Create Base64 string representations to store alongside
# metadata. This will allow us to preview the images.
from io import BytesIO
import math
import base64

target_width = 256

def resize_image(image_url):
    pil_image = Image.open(image_url)
    pil_image = pil_image.convert("RGB")
#    print(pil_image.mode)
    resized_pil_image = pil_image.resize((512, 512))
#    print("orig: " , pil_image.size)
#    print("resize: ",resized_pil_image.size)

    return resized_pil_image

def convert_image_to_base64(pil_image):
    image_data = BytesIO()
    # Convert the image.mode because the previous modes aren't supported for jpeg
    # This will convert source images from .jpg to .png format into single .JPEG format.
    pil_image.save(image_data,format = "JPEG")
    base64_string = base64.b64encode(image_data.getvalue()).decode("utf-8")
    return base64_string

resized_images = list(map(lambda img: resize_image(img),sample_image_urls))
base64_strings = list(map(lambda el : convert_image_to_base64(el),resized_images))
payloads['base64'] = base64_strings
print('payloads created')

#print(payloads)

#6. Import the model and tokenizer then run 
# all the images through it to create the embeddings.
from transformers import AutoImageProcessor, ResNetForImageClassification

processor = AutoImageProcessor.from_pretrained("microsoft/resnet-50")
model = ResNetForImageClassification.from_pretrained("microsoft/resnet-50")

inputs = processor(
    resized_images,
    return_tensors = "pt",
)

outputs = model(**inputs)
embeddings = outputs.logits
#print(embeddings)

embeddings_length = len(embeddings[0])


# 8. Create a collection called "stock_charts_images"
# This is the collection that our vector and metadata will be stored.
from qdrant_client.models import VectorParams,Distance

collection_name = "stock_charts_images"

# Check if collection already exists, if yes then pass else create new.
collection_exist = qclient.collection_exists(collection_name=collection_name)
if collection_exist:
    pass
else :
    collection = qclient.create_collection(
        collection_name = collection_name,
        vectors_config = VectorParams(
            size = embeddings_length,
            distance = Distance.COSINE
        )
    )
#    print(collection)


# 9. The Metadata must be uploaded as an array of objects so
# convert the dataframe to an array of objects before continuing.
payload_dicts = payloads.to_dict(
    orient = "records"
)
#print(payload_dicts)

# 10. Create the record. This is the payload (metadata) and the vector embeddings
# side by side. Because we have two arrays of data
from qdrant_client import models

records = [
    models.Record(
        id = idx,
        payload = payload_dicts[idx],
        vector = embeddings[idx]
    )
    for idx,_ in enumerate(payload_dicts)
]

# 11. Upload all the records to our collection.
qclient.upload_records(
    collection_name = collection_name,
    records = records
)
print('Records Inserted in Qdrant DB')





