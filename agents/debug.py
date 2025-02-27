import streamlit as st
st.set_page_config(page_title="ChartBuddyAI", layout="wide")# Expands content to the full screen width

from qdrant_client import QdrantClient
from io import BytesIO
import base64


collection_name = "stock_charts_images_clip"

client = QdrantClient(host ='localhost',port=6333,prefix="qdrant",timeout=60)

response, _ = client.scroll(collection_name=collection_name, limit=5)

for record in response:
    print(f"ID: {record.id}, Vector Length: {len(record.vector) if record.vector else 'None'}")


def get_vector_by_id(client, collection_name, record_id):
    response = client.retrieve(
        collection_name=collection_name,
        ids=[record_id]  # Use retrieve instead of scroll
    )

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

get_vector_by_id(client,collection_name,4)