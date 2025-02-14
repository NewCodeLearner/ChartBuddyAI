# ChartBuddyAI

ChartBuddyAI is your friendly companion for analyzing stock chart patterns using AI. With an intuitive interface, it helps investors and traders discover similar historical or real-time chart patterns to support data-driven decision-making.

## Introduction

ChartBuddyAI leverages advanced AI techniques to generate embeddings for stock chart images and match them against a curated vector database. Whether you're an experienced trader or just getting started, ChartBuddyAI simplifies the process of finding and comparing chart patterns.

## Purpose and Usage

### Purpose

- **Identify Similar Patterns:** Quickly find historical or current stock chart patterns that resemble your chart.
- **Enhance Decision-Making:** Provide actionable insights by comparing chart patterns and spotting trends.
- **Support Trading Strategies:** Use pattern matching to back up your analysis with data-driven evidence.

### How to Use ChartBuddyAI

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/NewCodeLearner/ChartBuddyAI
   cd ChartBuddyAI

2.Install Dependencies: Make sure you have Python installed, then run:
pip install -r requirements.txt

3.Run the Application: Start the Steamlit server:
streamlit run app.py

4.Upload or Select a Stock Chart Image:
Use the provided web interface to upload a stock chart image or choose one from the existing collection.

5.View Similar Chart Patterns:
ChartBuddyAI processes your image, generates its embedding, and displays similar stock charts from the database. For enhanced functionality, you can also trigger an agent that fetches real-time chart images from external sources.


## Technologies Used:
1.Python: The main language for backend development.
2.Streamlit: Web framework for building the user interface.
3.CLIP: Utilized for generating image embeddings and enabling similarity searches.
4.Vector Database: Integrated solution (such as Weaviate, Chroma, Pinecone, or Faiss) for storing and querying image embeddings.
5.Celery (Optional): For asynchronous processing of tasks, such as real-time data fetching.
6.HTML/CSS/JavaScript: For creating a responsive and user-friendly front-end interface.

