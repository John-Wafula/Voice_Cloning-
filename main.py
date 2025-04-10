import streamlit as st
import openai
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import os
import requests
import base64
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

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
def text_to_speech_with_speechify(text, voice_id="dc1f0dc1-ff98-4086-8687-40c0bb495965"):
    try:
        # Speechify API endpoint
        url = "https://api.sws.speechify.com/v1/audio/speech"
        
        # Headers for the API request
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer 9TO31l-2YltVh300iUA9pA-yLWItk8eI_NKXCJgfO6U="
        }
        
        # Request body
        data = {
            "input": text,
            "voice_id": voice_id
        }
        
        # Make the API request
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            # Parse the JSON response
            response_data = response.json()
            
            # Check if audio_data is in the response
            if "audio_data" in response_data:
                # Create a temporary file for the audio
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'.{response_data.get("audio_format", "wav")}')
                
                # Decode the base64 audio data and write to file
                audio_binary = base64.b64decode(response_data["audio_data"])
                temp_file.write(audio_binary)
                temp_file.close()
                
                return temp_file.name
            else:
                st.error(f"No audio data in response: {response_data}")
                return None
        else:
            st.error(f"Error generating speech: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error in text-to-speech conversion: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None

# Streamlit UI
st.title("Voice-Enabled AI Chatbot with Speechify")
st.write("Chat with AI using text or voice!")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    
    # Recording duration control
    recording_duration = st.slider("Recording Duration (seconds)", 1, 10, 5)
    
    # Voice selection
    voice_options = {
        "Default Voice": "dc1f0dc1-ff98-4086-8687-40c0bb495965"
        # Add more voices here if you know their IDs
    }
    
    selected_voice = st.selectbox(
        "Select Voice",
        options=list(voice_options.keys())
    )
    voice_id = voice_options[selected_voice]

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
        audio_file = text_to_speech_with_speechify(response_text, voice_id)
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
            audio_file = text_to_speech_with_speechify(response_text, voice_id)
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