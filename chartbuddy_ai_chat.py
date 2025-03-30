import streamlit as st
from groq import Groq
import base64
import os
from dotenv import load_dotenv
import requests

# Set up page configuration
st.title("ChartBuddy AI Chat")

# Display the selected or uploaded chart image if available.
# (Assumes that your "Search Similar Charts" page stores the image in st.session_state)
if 'selected_chart_image' in st.session_state:
    st.header("Selected Chart")
    st.image(st.session_state.selected_chart_image, use_container_width=True)
else:
    st.info("Please upload or select a chart from the 'Search Similar Charts' page.")

st.markdown("---")

# Define model details
models = {
    "llama3.2-11b-vision": {
        "name": "llama3.2-11b-vision",
        "tokens": 8192,
        "developer": "Meta",
    },
    "llama3-8b-8192": {
        "name": "LLaMA3-8b-Instruct",
        "tokens": 8192,
        "developer": "Meta",
    },
    "Gemini-1.5-Pro": {"name": "Gemini-1.5-Pro", "tokens": 8192, "developer": "Google"},
}



# Define Llama response function
def get_llama_response(user_message):
            GROQ_API_KEY = os.getenv("GROQ_API_KEY")
            client = Groq(api_key=GROQ_API_KEY)

            # Groq completion using Groq API Request: Call the chat.completions API endpoint.
            chat_completion = client.chat.completions.create(
                messages =[
                    {
                        "role":"user",
                        "content":[
                            {"type":"text", "text" : user_message},
                            {
                                "type":"image_url",
                                #we'll need to first encode our image to a base64 format string before passing it as the image_url in our API request
                                "image_url":{
                                    "url" : f"data:image/jpeg;base64,{base64.b64encode(st.session_state.selected_chart_image.read()).decode('utf-8')}"
                                }

                            }
                        ]
                    }
                ],
                model="llama-3.2-11b-vision-preview",
            )
            return chat_completion.choices[0].message.content

# Define Gemini response function
def get_gemini_response(prompt):
    GEMINI_API_URL = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY = os.getenv("GROQ_API_KEY")
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    response = requests.post(GEMINI_API_URL, headers=headers, params=params, json=payload)
    return response.json().get("candidates", [{}])[0].get("content", "Error: No response.")



# Layout for model selection and max_tokens slider
col1, col2 = st.columns(2)


with col1:
    model_option = st.selectbox(
        "Choose a model:",
        options=list(models.keys()),
        format_func=lambda x: models[x]["name"],
        index=0,  # Default to the first model in the list
    ) 
    # Display instructions
    st.info(f"You have selected **{model_option}** for your chat interactions.")

# Initialize chat history in session state if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

with col2:
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
                    "content": [{"type": "image_url", "image_url": {"url": image_data_url}}]
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
            #st.write("Conversation being sent:", conversation)

            # Create Groq client
            load_dotenv()  # This loads variables from .env into the environment
            if model_option == "llama3.2-11b-vision":
                response = get_llama_response(user_message)
            elif model_option =="Gemini-1.5-Pro":
                response = get_gemini_response(user_message)
                response = "Called from Gemini"
            
            # Append AI's response to chat history
            st.session_state.chat_history.append({
                   "role": "assistant",
                    #"content": chat_completion.choices[0].message.content
                    "content": response
             })

            # Clear the input box (optional) and refresh the page to show updated chat history.
            # Remove the key from session state to clear the input
            if "user_message" in st.session_state:
                del st.session_state["user_message"]
            st.rerun()

