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

# Initialize chat history in session state if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

st.header("Chat with AI")

# Display chat conversation
for message in st.session_state.chat_history:
    if message['role'] == 'user':
        st.markdown(f"**You:** {message['content']}")
    else:
        st.markdown(f"**AI:** {message['content']}")

# User input for new message
user_message = st.text_input("Enter your message", key="chat_input")

if st.button("Send"):
    if user_message:
        # Append user's message to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Call your API here (Ollama, Groq, etc.) to generate a response.
        # For this example, we'll simulate a response.
        simulated_response = f"Simulated response to: {user_message}"
        
        # Append AI's response to chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": simulated_response
        })
        
        # Clear the input box (optional) and refresh the page to show updated chat history.
        st.experimental_rerun()

