import streamlit as st
from groq import Groq
import base64
import os
from dotenv import load_dotenv

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

        # Build the conversation history for the API
        conversation = []

        # If an image is selected, add it to the conversation.
        # Here, we add the image as part of the first message.
        if 'selected_chart_image' in st.session_state:
            # Read image bytes, convert to base64 and build a data URL.
            image_bytes = st.session_state.selected_chart_image.read()
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            image_data_url = f"data:image/jpeg;base64,{base64_image}"
            # Optionally, add an image message at the beginning of the conversation.
            conversation.append({
                "role": "user",
                "content": f"[IMAGE]{image_data_url}[/IMAGE]"
            })
            # Reset the file pointer so the image can be used/displayed again.
            st.session_state.selected_chart_image.seek(0)
        
        # Append all text messages from chat history
        for msg in st.session_state.chat_history:
            conversation.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # For debugging: print the conversation payload
        st.write("Conversation being sent:", conversation)
        
        # Call your API here (Ollama, Groq, etc.) to generate a response.
        # For this example, we'll simulate a response.
        #simulated_response = f"Simulated response to: {user_message}"

        # Create Groq client
        load_dotenv()  # This loads variables from .env into the environment
        GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=GROQ_API_KEY)
        
        # Groq completion using Groq API Request: Call the chat.completions API endpoint.
        chat_completion = client.chat.completions.create(
            messages =conversation,
            model="llama-3.2-11b-vision-preview",
        )
        
        # Append AI's response to chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": chat_completion.choices[0].message.content
        })
        
        # Clear the input box (optional) and refresh the page to show updated chat history.
        st.rerun()

