import streamlit as st
import openai
import sounddevice as sd
import soundfile as sf
import numpy as np
import tempfile
import os
from scipy.io.wavfile import write as write_wav
import time
import requests
from io import BytesIO

# Configure OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'voice_id' not in st.session_state:
    st.session_state.voice_id = None
if 'voice_name' not in st.session_state:
    st.session_state.voice_name = None
if 'elevenlabs_api_key' not in st.session_state:
    st.session_state.elevenlabs_api_key = "sk_70e497669c4fc9c9db47626a33be33be13cc3999aca6abbc"

def record_audio(duration=5, sample_rate=44100):
    """Record audio from microphone"""
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
    sd.wait()
    return recording

def save_audio(recording, sample_rate=44100):
    """Save recorded audio to a temporary file"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        write_wav(temp_file.name, sample_rate, recording)
        return temp_file.name

def transcribe_audio(audio_file):
    """Transcribe audio using OpenAI Whisper"""
    with open(audio_file, 'rb') as file:
        transcript = openai.audio.transcriptions.create(
            model="whisper-1",
            file=file
        )
    return transcript.text

def get_available_voices():
    """Get list of available ElevenLabs voices"""
    try:
        headers = {
            "xi-api-key": st.session_state.elevenlabs_api_key,
            "Accept": "application/json"
        }
        response = requests.get(
            "https://api.elevenlabs.io/v1/voices",
            headers=headers
        )
        if response.status_code == 200:
            voices_data = response.json()
            return {voice["name"]: voice["voice_id"] for voice in voices_data["voices"]}
        else:
            st.error(f"Error fetching voices: {response.status_code} - {response.text}")
            return {}
    except Exception as e:
        st.error(f"Error fetching voices: {str(e)}")
        return {}

def text_to_speech_with_voice(text, voice_id):
    """Convert text to speech using ElevenLabs API"""
    try:
        headers = {
            "xi-api-key": st.session_state.elevenlabs_api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        response = requests.post(
            f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"Error generating speech: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Error generating speech: {str(e)}")
        return None

# Streamlit UI
st.title("Voice-Enabled AI Chatbot with ElevenLabs Voices")
st.write("Chat with AI using text or voice!")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    recording_duration = st.slider("Recording Duration (seconds)", 1, 10, 5)
    
    st.header("ElevenLabs Configuration")
    elevenlabs_key = st.text_input("Enter ElevenLabs API Key", value=st.session_state.elevenlabs_api_key, type="password")
    if elevenlabs_key:
        st.session_state.elevenlabs_api_key = elevenlabs_key
        
        # Voice selection
        st.subheader("Voice Selection")
        available_voices = get_available_voices()
        if available_voices:
            selected_voice = st.selectbox(
                "Choose a voice",
                options=list(available_voices.keys()),
                index=0 if available_voices else None
            )
            if selected_voice:
                st.session_state.voice_id = available_voices[selected_voice]
                st.session_state.voice_name = selected_voice
        else:
            st.warning("Please enter a valid ElevenLabs API key to see available voices")

# Main chat interface
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Text input
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        )
        response_text = response.choices[0].message.content
        st.write(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
        
        # Generate speech with selected voice if available
        if st.session_state.voice_id and st.session_state.elevenlabs_api_key:
            audio = text_to_speech_with_voice(response_text, st.session_state.voice_id)
            if audio:
                st.audio(audio, format="audio/mp3")

# Voice input button
if st.button("🎤 Record Voice Input"):
    with st.spinner("Recording..."):
        recording = record_audio(duration=recording_duration)
        audio_file = save_audio(recording)
        
        # Transcribe the audio
        transcript = transcribe_audio(audio_file)
        st.session_state.messages.append({"role": "user", "content": transcript})
        
        with st.chat_message("user"):
            st.write(f"🎤 {transcript}")
        
        # Get AI response
        with st.chat_message("assistant"):
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            )
            response_text = response.choices[0].message.content
            st.write(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
            # Generate speech with selected voice if available
            if st.session_state.voice_id and st.session_state.elevenlabs_api_key:
                audio = text_to_speech_with_voice(response_text, st.session_state.voice_id)
                if audio:
                    st.audio(audio, format="audio/mp3")
        
        # Clean up temporary files
        os.unlink(audio_file)

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.experimental_rerun() 