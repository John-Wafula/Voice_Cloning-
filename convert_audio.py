import requests
import os
import pygame
import json
import base64
import io

def speechify_tts(text: str, voice_id="dc1f0dc1-ff98-4086-8687-40c0bb495965"):
    try:
        # Create output directory if it doesn't exist
        os.makedirs("media/audio", exist_ok=True)
        
        # API endpoint and headers
        url = "https://api.sws.speechify.com/v1/audio/speech"
        headers = {
            "Authorization": "Bearer 9TO31l-2YltVh300iUA9pA-yLWItk8eI_NKXCJgfO6U=",
            "Content-Type": "application/json"
        }
        
        # Request body
        data = {
            "input": text,
            "voice_id": voice_id
        }
        
        # Make the API call
        response = requests.post(url, headers=headers, json=data)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            json_response = response.json()
            
            # Get the audio data and format from the response
            audio_data = json_response.get("audio_data")
            audio_format = json_response.get("audio_format", "wav")
            
            if not audio_data:
                print("No audio data found in the response")
                return None
            
            # The example shows "audio_data" as a placeholder string rather than actual base64
            # In a real response, this would be the base64-encoded audio
            # If this is just an example schema and not the actual response, 
            # you may need to examine the actual API response
            
            try:
                # Decode the base64 audio data
                decoded_audio = base64.b64decode(audio_data)
                
                # Save the audio file
                output_path = os.path.join("media/audio", f"response.{audio_format}")
                with open(output_path, "wb") as f:
                    f.write(decoded_audio)
                
                # Initialize pygame mixer
                pygame.mixer.init()
                
                # Load and play the audio
                pygame.mixer.music.load(output_path)
                pygame.mixer.music.play()
                
                # Wait until playback finishes
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                
                print(f"Audio generated and played successfully")
                return output_path
                
            except Exception as e:
                print(f"Error processing audio data: {str(e)}")
                # If we can't decode the base64, it might be an example/placeholder
                print("Note: The 'audio_data' value in your example appears to be a placeholder, not actual base64 audio data")
                return None
        else:
            print(f"API request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
    except Exception as e:
        print(f"Error in speechify_tts: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Example usage
if __name__ == "__main__":
    speechify_tts("Mumtumie Andrew Pesa , Mimi Simba Mwenyewe nitaperform")