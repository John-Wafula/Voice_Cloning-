# Voice-Enabled AI Chatbot

A Streamlit application that provides a chatbot interface with both text and voice capabilities. The app uses OpenAI's GPT-3.5 for chat responses, Whisper for speech-to-text, and Text-to-Speech for voice output.

## Features

- Text-based chat interface
- Voice input recording
- Speech-to-text transcription
- Text-to-speech response
- Adjustable recording duration
- Chat history
- Clear chat functionality

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Run the Streamlit app:
```bash
streamlit run app.py
```

## Usage

1. **Text Chat**:
   - Type your message in the text input field at the bottom
   - Press Enter to send

2. **Voice Chat**:
   - Click the "🎤 Record Voice Input" button
   - Speak for the duration specified in the settings
   - The app will transcribe your voice and respond both in text and voice

3. **Settings**:
   - Adjust the recording duration using the slider in the sidebar

4. **Clear Chat**:
   - Click the "Clear Chat" button to start a new conversation

## Requirements

- Python 3.7+
- Microphone for voice input
- Speakers for voice output
- Internet connection for OpenAI API access 