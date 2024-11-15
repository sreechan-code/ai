import os
import streamlit as st
import google.generativeai as genai
from gtts import gTTS

# Configure the API key directly
genai.configure(api_key="AIzaSyBN9ZlpzLLoHklPYo7d_7y7Uw9UW1wlE9E")

# Function to load the Gemini Pro model and get a response
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

def get_gemini_response(question):
    try:
        response = chat.send_message(question, stream=True)
        return response
    except ValueError as e:
        st.error(f"Error in generating response: {str(e)}")
        return None

# Initialize Text-to-Speech (TTS) engine (fallback to gTTS if pyttsx3 fails)
def speak_text(text):
    # Use gTTS (Google Text-to-Speech) as fallback in case pyttsx3 is unavailable
    tts = gTTS(text=text, lang='en')
    tts.save("response.mp3")
    os.system("mpg321 response.mp3")  # Make sure mpg321 is installed to play audio

# Check if running in cloud or locally (for microphone functionality)
in_cloud = "STREAMLIT_CLOUD" in os.environ  # Change this based on how the cloud environment is configured

# Streamlit app configuration
st.set_page_config(page_title="eleAi")

# CSS for positioning the logo on the top left
st.markdown("""
    <style>
    .top-left-logo {
        position: absolute;
        top: 10px;
        left: 10px;
        width: 50px;
        height: auto;
    }
    h1 {
        text-align: center;
        color: cyan;
        margin-top: 0;
    }
    .stTextInput, .stButton, .stMarkdown {
        font-size: 18px;
    }
    .jarvis-container {
        border: 2px solid cyan;
        border-radius: 10px;
        padding: 20px;
        background-color: #1e1e1e;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Display team logo in the top-left corner
st.sidebar.image("teamlogo.png", use_column_width=True)

# Streamlit app title
st.markdown("<h1>Welcome to eleAi</h1>", unsafe_allow_html=True)

# Options for input mode: Text or Voice (only available locally)
if not in_cloud:
    mode = st.radio("Select Input Mode:", options=["Speak", "Type"], index=1)
else:
    mode = "Type"  # Disable "Speak" mode in cloud

if mode == "Type":
    input_text = st.text_input("Type your question and press Enter:", key="input")
    
    if input_text:
        response = get_gemini_response(input_text)
        if response:
            st.subheader("Response:")
            full_response = ""
            for chunk in response:
                # Ensure the chunk has the attribute 'text' and handle any error in content access
                if hasattr(chunk, 'text') and chunk.text:
                    st.write(chunk.text)
                    full_response += chunk.text
                else:
                    st.warning("No valid response received. The model might have detected copyrighted content.")

            # Speak the response if desired
            if full_response:
                speak_text(full_response)

# If voice input was selected and not in cloud
elif mode == "Speak" and not in_cloud:
    import speech_recognition as sr
    try:
        with sr.Microphone() as source:
            st.write("Listening...")
            recognizer = sr.Recognizer()
            audio = recognizer.listen(source)
            input_text = recognizer.recognize_google(audio)
            st.write(f"You said: {input_text}")

            if input_text:
                response = get_gemini_response(input_text)
                if response:
                    st.subheader("Response:")
                    full_response = ""
                    for chunk in response:
                        # Ensure the chunk has the attribute 'text' and handle any error in content access
                        if hasattr(chunk, 'text') and chunk.text:
                            st.write(chunk.text)
                            full_response += chunk.text
                    # Speak the response if desired
                    if full_response:
                        speak_text(full_response)
    except Exception as e:
        st.error(f"Error occurred while processing voice input: {e}")
