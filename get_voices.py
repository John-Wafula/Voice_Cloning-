import requests

# Speechify API endpoint for voices
url = "https://api.sws.speechify.com/v1/voices"

# Your API token
token = "9TO31l-2YltVh300iUA9pA-yLWItk8eI_NKXCJgfO6U="

# Headers for the API request
headers = {
    "Authorization": f"Bearer {token}"
}

try:
    # Make the API request
    response = requests.get(url, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        voices = response.json()
        print("\nSearching for voice ID 'dc1f0dc1-ff98-4086-8687-40c0bb495965':")
        print("----------------")
        found = False
        for voice in voices:
            if voice.get('id') == 'dc1f0dc1-ff98-4086-8687-40c0bb495965':
                found = True
                print(f"Name: {voice.get('name', 'N/A')}")
                print(f"ID: {voice.get('id', 'N/A')}")
                print(f"Language: {voice.get('language', 'N/A')}")
                print(f"Gender: {voice.get('gender', 'N/A')}")
                print("----------------")
        
        if not found:
            print("Voice ID not found in the available voices.")
            print("\nAvailable voice IDs:")
            for voice in voices:
                print(f"ID: {voice.get('id', 'N/A')}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"An error occurred: {str(e)}") 