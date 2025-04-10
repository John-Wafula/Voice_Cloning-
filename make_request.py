import requests
import base64
import json
import os
from pathlib import Path
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def ensure_output_dir():
    """Create output directory if it doesn't exist."""
    output_dir = Path.home() / "Documents" / "voice_clone_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def save_base64_audio(base64_data, output_path):
    """Save base64 encoded audio data to a file."""
    try:
        # Decode base64 data
        audio_bytes = base64.b64decode(base64_data)
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the audio data
        with open(output_path, 'wb') as f:
            f.write(audio_bytes)
        
        # Verify file was written and get size
        if output_path.exists():
            size_kb = output_path.stat().st_size / 1024
            logging.info(f"Successfully saved audio file to {output_path}")
            logging.info(f"File size: {size_kb:.2f} KB")
            return True
        else:
            logging.error(f"File was not created at {output_path}")
            return False
            
    except PermissionError as e:
        logging.error(f"Permission denied when saving to {output_path}.")
        logging.error(f"Error details: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Failed to save base64 audio data: {str(e)}")
        return False

def download_audio_from_url(url, output_path):
    """Download audio from URL and save to file."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        # Verify file was written and get size
        if output_path.exists():
            size_kb = output_path.stat().st_size / 1024
            logging.info(f"Successfully downloaded audio to {output_path}")
            logging.info(f"File size: {size_kb:.2f} KB")
            return True
        else:
            logging.error(f"File was not created at {output_path}")
            return False
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to download audio: {str(e)}")
        return False
    except PermissionError as e:
        logging.error(f"Permission denied when saving to {output_path}")
        logging.error(f"Error details: {str(e)}")
        return False
    except Exception as e:
        logging.error(f"Failed to save downloaded audio: {str(e)}")
        return False

def main():
    # Create timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get output directory
    output_dir = ensure_output_dir()
    output_path = output_dir / f"output_{timestamp}.mp3"
    
    # API configuration
    url = "https://api.speechify.com/api/tts/clone"
    
    # Get API key from environment variable
    api_key = os.getenv('SPEECHIFY_API_KEY')
    if not api_key:
        logging.error("SPEECHIFY_API_KEY environment variable not set")
        return
        
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    # Example payload - adjust according to Speechify API requirements
    payload = {
        "text": "Hello, this is a test of voice cloning.",
        "voice_id": "your_voice_id",  # Replace with actual voice ID
        "output_format": "mp3"
    }
    
    try:
        # Test DNS resolution first
        try:
            from urllib.parse import urlparse
            import socket
            domain = urlparse(url).netloc
            socket.gethostbyname(domain)
        except socket.gaierror as e:
            logging.error(f"DNS resolution failed for {domain}: {str(e)}")
            logging.info("Please check your internet connection and DNS settings")
            return
            
        logging.info("Making request to Speechify API...")
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        logging.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Handle base64 encoded audio
            if "audio_data" in data:
                if save_base64_audio(data["audio_data"], output_path):
                    logging.info("Successfully processed base64 audio data")
                else:
                    logging.error("Failed to save base64 audio data")
                    
            # Handle audio URL
            elif "audio_url" in data:
                if download_audio_from_url(data["audio_url"], output_path):
                    logging.info("Successfully downloaded audio from URL")
                else:
                    logging.error("Failed to download audio from URL")
                    
            else:
                logging.error("No audio data or URL found in response")
                
        elif response.status_code == 401:
            logging.error("Authentication failed. Please check your API key.")
        elif response.status_code == 403:
            logging.error("Access forbidden. Please check your API permissions.")
        else:
            logging.error(f"API request failed with status {response.status_code}")
            logging.error(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError as e:
        logging.error(f"Connection error: {str(e)}")
        logging.info("Please check your internet connection")
    except requests.exceptions.Timeout as e:
        logging.error(f"Request timed out: {str(e)}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed: {str(e)}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main() 