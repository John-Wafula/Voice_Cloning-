from gtts import gTTS
import os
import pygame

def text_to_speech(text: str):
    try:
        # Create output directory if it doesn't exist
        os.makedirs("media/audio", exist_ok=True)
        
        # Set the output path
        output_path = os.path.join("media/audio", "response.wav")
        
        # Generate speech using Google's TTS
        tts = gTTS(text=text, lang='en', slow=False)
        
        # Save as mp3 first (gTTS doesn't support direct WAV)
        temp_mp3 = os.path.join("media/audio", "temp.mp3")
        tts.save(temp_mp3)
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Load and play the audio
        pygame.mixer.music.load(temp_mp3)
        pygame.mixer.music.play()
        
        # Wait until playback finishes
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        print(f"Audio generated and played successfully")
        return temp_mp3
        
    except Exception as e:
        print(f"Error in text_to_speech: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    text_to_speech("Hi there how are you")