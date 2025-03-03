import streamlit as st
from groq import Groq
import base64

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
        #simulated_response = f"Simulated response to: {user_message}"

        # Create Groq client
        client = Groq()
        
        # Groq completion using Groq API Request: Call the chat.completions API endpoint.
        chat_completion = client.chat.completions.create(
            messages =[
                {
                    "role":"user",
                    "content":[
                        {"type":"text", "text" : "Whats in this image? which candlestick pattern do you recognize in this chart?"},
                        {
                            "type":"image_url",
                            #we'll need to first encode our image to a base64 format string before passing it as the image_url in our API request
                            "image_url":{
                                "url" : base64.b64encode(st.session_state.selected_chart_image).decode('utf-8')
                            }

                        }
                    ]
                }
            ],
            model="llama-3.2-11b-vision-preview",
        )
        
        # Append AI's response to chat history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": chat_completion.choices[0].message.content
        })
        
        # Clear the input box (optional) and refresh the page to show updated chat history.
        st.rerun()

