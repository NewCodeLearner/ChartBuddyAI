import streamlit as st

# Set up page configuration
#st.set_page_config(page_title="ChartBuddy AI Chat", layout="wide")
st.title("ChartBuddy AI Chat")

# Display the selected or uploaded chart image if available.
# (Assumes that your "Search Similar Charts" page stores the image in st.session_state)
if 'selected_chart_image' in st.session_state:
    st.header("Selected Chart")
    st.image(st.session_state.selected_chart_image, use_container_width=True)
else:
    st.info("Please upload or select a chart from the 'Search Similar Charts' page.")

st.markdown("---")