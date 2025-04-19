import streamlit as st
st.set_page_config(page_title="ChartBuddyAI", layout="wide")# Expands content to the full screen width
from dotenv import load_dotenv

load_dotenv(override=True)


pages = {
    "Your account": [
        st.Page("search_similar_charts.py", title="Search Similar Charts"),
        st.Page("chartbuddy_ai_chat.py", title="Chat with AI for Similar Charts")

    ],
  #  "Resources": [
   #     st.Page("agents/agent_new.py", title="Ingest New Charts")
    #],
}

pg = st.navigation(pages)
pg.run()







