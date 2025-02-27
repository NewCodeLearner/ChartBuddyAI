import streamlit as st
st.set_page_config(page_title="ChartBuddyAI", layout="wide")# Expands content to the full screen width

from qdrant_client import QdrantClient
from io import BytesIO
import base64


collection_name = "stock_charts_images_clip"

client = QdrantClient(host ='localhost',port=6333,prefix="qdrant",timeout=60)

response, _ = client.scroll(collection_name=collection_name, limit=5)
#print(response)

def get_vector_by_id(client, collection_name, record_id):
    response = client.retrieve(
        collection_name=collection_name,
        ids=[0]  # Use retrieve instead of scroll
    )

    print(response[0].vector)

    if response:
        vector = response[0].vector
        if vector:
            print(f"✅ Vector retrieved for ID {record_id}: {vector[:5]}")
            return vector
        else:
            print(f"❌ No vector found for ID: {record_id}")
    else:
        print(f"❌ No record found for ID: {record_id}")

    return None

get_vector_by_id(client,collection_name,1)

collection_info = client.get_collection(collection_name=collection_name)
#print(collection_info)

info = client.get_collection(collection_name)
print("Vectors Count:", info.vectors_count)
print("Indexed Vectors Count:", info.indexed_vectors_count)


