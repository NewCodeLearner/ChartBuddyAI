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

# Define a system prompt that tells the model its role.
SYSTEM_PROMPT = (
    "You are ChartBuddy, an expert assistant in stock chart analysis. "
    "Your role is to analyze stock charts, identify candlestick patterns, and provide "
    "detailed, actionable insights based on the chart data. Answer the user's questions "
    "in a clear, concise, and informative manner."
    "The stock name is located at the top left corner of the chart."""
    "If You cannot identify the stock name respond with stock name not readable."
)

# Define the centralized message preparation.
def prepare_messages(user_message: str) -> list:
    """
    Prepare the messages payload for LLM APIs based on whether an image is present.
    
    Returns:
        list: A list of message dictionaries.
    """
    messages = []
            
    # If an image is selected, add it to the conversation.
    # Here, we add the image as part of the first message.
    if 'selected_chart_image' in st.session_state:
        # Read image bytes, convert to base64 and build a data URL.
        image_bytes = st.session_state.selected_chart_image.read()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        image_data_url = f"data:image/jpeg;base64,{base64_image}"

        # Merge the system prompt into the user message when an image is present.
        combined_text = SYSTEM_PROMPT + "\nUser: " + user_message

        # Optionally, add an image message at the beginning of the conversation.
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": combined_text},
                {"type": "image_url", "image_url": {"url": image_data_url}}
                ]
        })
        # Reset the file pointer so the image can be used/displayed again.
        st.session_state.selected_chart_image.seek(0)
    else:
        # If no image is present, include system and user messages separately.
        messages.append({"role": "system", "content": SYSTEM_PROMPT})
        messages.append({"role": "user", "content": user_message})
    return messages



# Define Llama response function
def get_llama_response(user_message):
            GROQ_API_KEY = os.getenv("GROQ_API_KEY")
            client = Groq(api_key=GROQ_API_KEY)

            # Prepare the messages payload.
            messages = prepare_messages(user_message)

            # Groq completion using Groq API Request: Call the chat.completions API endpoint.
            chat_completion = client.chat.completions.create(
                messages = messages,
                model="llama-3.2-11b-vision-preview",
            )
            return chat_completion.choices[0].message.content

# Define Gemini response function
def get_gemini_response(prompt):
    GEMINI_API_URL = os.getenv("GROQ_API_URL")
    GEMINI_API_KEY = os.getenv("GROQ_API_KEY")
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}

        # Incorporate the system prompt into the payload.
    prompt = SYSTEM_PROMPT + "\nUser: " + user_message
  
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

    # Use a form to handle the chat input so that it resets after submission.
    with st.form(key="chat_form", clear_on_submit=True):
        user_message = st.text_input("Enter your message", key="chat_input")
        submit_button = st.form_submit_button(label="Send")

   
        if submit_button and user_message:
            # Append user's message to chat history
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_message
            })

            # For debugging, can inspect the prepared messages.
            messages = prepare_messages(user_message)
            #st.write("Prepared messages:", messages)


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
                    "content": response
             })

            # Clear the input box (optional) and refresh the page to show updated chat history.
            st.rerun()

