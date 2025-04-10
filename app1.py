import streamlit as st
import openai
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import os
import requests
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize session state for messages and Speechify API key
if "messages" not in st.session_state:
    st.session_state.messages = []
if "speechify_api_key" not in st.session_state:
    st.session_state.speechify_api_key = ""

# Function to record audio
def record_audio(duration=5, sample_rate=44100):
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    return recording

# Function to save audio to a temporary file
def save_audio(recording, sample_rate=44100):
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    sf.write(temp_file.name, recording, sample_rate)
    return temp_file.name

# Function to transcribe audio using OpenAI Whisper
def transcribe_audio(audio_file):
    with open(audio_file, 'rb') as file:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=file
        )
    return transcript.text

# Function to convert text to speech using Speechify
def text_to_speech_with_speechify(text, voice="en-US-Neural2-F"):
    try:
        # Speechify API endpoint
        url = "https://api.speechify.ai/v2/tts"
        
        # Headers for the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {st.session_state.speechify_api_key}"
        }
        
        # Request body
        data = {
            "text": text,
            "voice": voice,
            "format": "mp3"
        }
        
        # Make the API request
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            # Create a temporary file for the audio
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            temp_file.write(response.content)
            temp_file.close()
            return temp_file.name
        else:
            st.error(f"Error generating speech: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error in text-to-speech conversion: {str(e)}")
        return None

# Function to get available voices from Speechify
def get_available_voices():
    try:
        url = "https://api.speechify.ai/v2/voices"
        headers = {
            "Authorization": f"Bearer {st.session_state.speechify_api_key}",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            voices = response.json()
            return {voice["name"]: voice["id"] for voice in voices}
        else:
            st.error(f"Error fetching voices: {response.status_code} - {response.text}")
            return {}
    except Exception as e:
        st.error(f"Error fetching voices: {str(e)}")
        return {}

# Streamlit UI
st.title("Voice-Enabled AI Chatbot with Speechify")
st.write("Chat with AI using text or voice!")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    
    # Recording duration control
    recording_duration = st.slider("Recording Duration (seconds)", 1, 10, 5)
    
    # Speechify API key input
    speechify_api_key = st.text_input(
        "Enter Speechify API Key",
        value=st.session_state.speechify_api_key,
        type="password"
    )
    if speechify_api_key:
        st.session_state.speechify_api_key = speechify_api_key
    
    # Voice selection
    voices = get_available_voices()
    if voices:
        selected_voice = st.selectbox(
            "Select Voice",
            options=list(voices.keys())
        )
    else:
        selected_voice = "Default Voice"
        st.warning("No voices available. Please check your API key.")

# Main chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "audio" in message:
            st.audio(message["audio"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Get AI response
    with st.chat_message("assistant"):
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        )
        response_text = response.choices[0].message.content
        st.write(response_text)
        
        # Convert response to speech
        if st.session_state.speechify_api_key and voices:
            audio_file = text_to_speech_with_speechify(response_text, voices[selected_voice])
            if audio_file:
                st.audio(audio_file)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text,
                    "audio": audio_file
                })
        else:
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_text
            })

# Voice input button
if st.button("🎤 Record Voice Input"):
    with st.spinner("Recording..."):
        recording = record_audio(duration=recording_duration)
        audio_file = save_audio(recording)
        
        # Transcribe the audio
        transcript = transcribe_audio(audio_file)
        st.write(f"🎤 {transcript}")
        
        # Add transcribed text to chat
        st.session_state.messages.append({"role": "user", "content": transcript})
        
        # Get AI response for voice input
        with st.chat_message("assistant"):
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            response_text = response.choices[0].message.content
            st.write(response_text)
            
            # Convert response to speech
            if st.session_state.speechify_api_key and voices:
                audio_file = text_to_speech_with_speechify(response_text, voices[selected_voice])
                if audio_file:
                    st.audio(audio_file)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text,
                        "audio": audio_file
                    })
            else:
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response_text
                })
        
        # Clean up temporary files
        os.unlink(audio_file)

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.experimental_rerun()
