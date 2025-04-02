#Code file to import documents,images into Qdrant database
from langchain_community.vectorstores import Qdrant
from qdrant_client import QdrantClient,models
from transformers import CLIPModel, CLIPProcessor
from qdrant_client.http.models import Vector
from qdrant_client.models import VectorParams,Distance
from src.image_utils import enhance_image
import streamlit as st
import os,math,base64
from io import BytesIO
from pandas import DataFrame
from PIL import Image
from dotenv import load_dotenv



# 1. Create Qdrant Client
def load_qdrant_client():
    return QdrantClient(host ='localhost',port=6333,prefix="qdrant",timeout=60)


# 2. Fetch All images in the dataset
def load_images_and_payloads(base_directory="img"):

    all_image_urls = os.listdir(base_directory)
    #print(all_image_urls[:5])

    #concat image urls with base directory to construct full dir path.
    sample_image_urls = list(map(lambda item : f"{base_directory}/{item}",all_image_urls))


    # 3. Create a dataframe to store the image's metadata
    payloads = DataFrame.from_records({"image_url": sample_image_urls})
    payloads["type"] = "stockchart"


    # 4. Create PIL (Python Imaging Library) image from each of the local URLs.
    # PIL provides a wide range of functions for image processing, such as resizing, cropping, rotating, and applying filters.
    images =  list(map(lambda imgurl : Image.open(imgurl),payloads['image_url']))
    return images,payloads,sample_image_urls



# 5. Create Base64 string representations to store alongside
# metadata. This will allow us to preview the images.
def resize_and_enhance_images(sample_image_urls):
    def resize_image(image_url):
        pil_image = Image.open(image_url)
        pil_image = pil_image.convert("RGB")
        resized_pil_image = pil_image.resize((512, 512))
        resized_pil_image = enhance_image(resized_pil_image)
        return resized_pil_image
    resized_images = list(map(lambda img: resize_image(img),sample_image_urls))
    return resized_images

def convert_images_to_base64(resized_images):
    def convert_image_to_base64(pil_image):
        image_data = BytesIO()
        # Convert the image.mode because the previous modes aren't supported for jpeg
        # This will convert source images from .jpg to .png format into single .JPEG format.
        pil_image.save(image_data,format = "JPEG")
        base64_string = base64.b64encode(image_data.getvalue()).decode("utf-8")
        return base64_string
    base64_strings = list(map(convert_image_to_base64,resized_images))
    return base64_strings


#6. Import the model and tokenizer then run 
# all the images through it to create the embeddings.
#code changes for the CLIP model usage
def load_clip_model():
    return CLIPModel.from_pretrained("openai/clip-vit-base-patch32"), CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def load_clip_embeddings(resized_images):
    model, processor = load_clip_model()
    inputs = processor(images=resized_images, return_tensors="pt")
    embeddings = model.get_image_features(**inputs) # Get embeddings
    # ✅ Convert tensor to list before storing in Qdrant
    embeddings = embeddings.cpu().detach().numpy().tolist()
    return embeddings

# 9. The Metadata must be uploaded as an array of objects so
# convert the dataframe to an array of objects before continuing.

def create_records(qclient,payloads, embeddings,collection_name):
    payload_dicts = payloads.to_dict(orient = "records")
    #print(payload_dicts)

    # Fetch existing image URLs or base64 strings from Qdrant
    existing_image_urls = set(
    point.payload.get("image_url")
    for point in qclient.scroll(
        collection_name=collection_name,
        scroll_filter=models.Filter(must=[]),  # Empty filter to get all points
        limit=10000  # Set based on your dataset size
    )[0]
    )
    existing_base64_hashes = set(
    point.payload.get("base64")
    for point in qclient.scroll(
        collection_name=collection_name,
        scroll_filter=models.Filter(must=[]),
        limit=10_000
    )[0]
    )

    # 10. Create the record. This is the payload (metadata) and the vector embeddings
    # side by side. Because we have two arrays of data
    records = [
        models.Record(
            id = idx,
            payload = payload_dicts[idx],
            vector = list(map(float, embeddings[idx]))  # Force float conversion
        )
        for idx,record in enumerate(payload_dicts)
        if record['image_url'] not in existing_image_urls
            and record['base64'] not in existing_base64_hashes
    ]
    return records

def ingest_records_with_progress(qclient,collection_name,records, batch_size=100):
    total_records = len(records)
    total_batches = math.ceil(total_records / batch_size)
    progress_bar = st.progress(0)
    
    # Get the current number of points in the collection
    current_count = qclient.count(collection_name=collection_name).count
    response = None  # Initialize response before the loop
    
    for i in range(total_batches):
        start = i * batch_size
        end = start + batch_size
        batch_records = records[start:end]
        if batch_records:
            response = qclient.upsert(
                collection_name=collection_name,
                points=[
                    models.PointStruct(
                        id=record.id + current_count,  # Offset new IDs by current count
                        vector=record.vector,
                        payload=record.payload
                    )
                    for record in batch_records
                ]
            )
            print(f"Inserted {len(batch_records)} new images.")
        else:
            print("No new records to insert — all images are already in Qdrant.")
        
        # Update progress: progress is a value between 0 and 1.
        progress_bar.progress((i + 1) / total_batches)
       
    if response:
        st.success(f"Ingestion complete! Inserted {len(records)} new images.")
    else:
        st.warning("No new images were added to the database.")




def ingest_all_charts(batch_size=100):
    """
    Performs the full ingestion workflow:
      - Loads images and payloads from the base directory.
      - Resizes, enhances, and converts images to base64.
      - Computes embeddings using CLIP.
      - Creates Qdrant records.
      - Creates (or verifies) the collection.
      - Ingests all records in batches with a progress bar.
      
    Returns the response from the final upsert call.
    """
    # Create Qdrant client and print its info for debugging.
    qclient = load_qdrant_client()
    print(qclient.info())

    # Step 1: Load images and payloads from the base directory.
    images, payloads, sample_image_urls = load_images_and_payloads("img")

    # Step 2: Resize and enhance images.
    resized_images = resize_and_enhance_images(sample_image_urls)

    # Step 3: Convert enhanced images to Base64 strings and add to payload.
    base64_strings=convert_images_to_base64(resized_images)
    payloads['base64'] = base64_strings
    print('base64 payloads created')

    # Step 4: Get embeddings using CLIP.
    embeddings = load_clip_embeddings(resized_images)
    print('embeddings created')

    # Step 5: Create records combining payload and embeddings.
    collection_name = os.getenv('COLLECTION_NAME')
    print('print ', collection_name)
    records = create_records(qclient,payloads, embeddings,collection_name)
    print('records created')

    # Step 6: This is the collection that our vector and metadata will be stored.
    # Check if collection already exists, if yes then pass else create new.
    collection_exist = qclient.collection_exists(collection_name=collection_name)

    if collection_exist:
        pass
    else :
        collection = qclient.create_collection(
            collection_name = collection_name,
            vectors_config = VectorParams(
                size = 512,
                distance = Distance.COSINE
            )
        )
    #    print(collection)

    # Ensure collection is indexed immediately
    qclient.update_collection(
        collection_name=collection_name,
        optimizers_config=models.OptimizersConfigDiff(indexing_threshold=0)  # Force immediate indexing
    )

    # Step 7: Ingest the records with progress reporting.
    response =ingest_records_with_progress(qclient, collection_name, records,batch_size=batch_size)
    print(f"Qdrant upload response: {response}")
    print('Records Inserted in Qdrant DB')
    return response

if __name__ == "__main__":
    ingest_all_charts()