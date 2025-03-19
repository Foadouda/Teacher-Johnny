import pygame
import requests
import json
import os
import sys
from io import BytesIO

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from project_backend.core.settings import Settings

# Initialize the Settings class
settings = Settings()

# Set up your ElevenLabs API key
VOICE_ID = "pqHfZKP75CvOlQylNhV4"  # Replace with a valid voice ID

# Function to convert text to speech using ElevenLabs
def speak_text(text: str) -> None:
    pygame.mixer.init()

    try:
        # ElevenLabs API endpoint
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

        headers = {
            "xi-api-key": settings.TTS_API_KEY,  # Use the settings instance
            "Content-Type": "application/json"
        }

        data = {
            "text": text,
            "model_id": "eleven_turbo_v2",  # Use ElevenLabs' fastest model
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.7}
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            audio_data = BytesIO(response.content)
            pygame.mixer.music.load(audio_data)
            pygame.mixer.music.play()

            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
        else:
            print(f"❌ Error: {response.json()}")

    except Exception as e:
        print(f"Error in TTS: {e}")

# Function to read scripts from a JSON file
def read_scripts_from_json(json_file: str) -> list:
    if not os.path.exists(json_file):
        print(f"❌ File not found: {json_file}")
        sys.exit(1)

    with open(json_file, 'r') as file:
        data = json.load(file)
        scripts = [slide.get('script', '') for slide in data.get('slides', [])]
        return scripts

if __name__ == "__main__":
    json_file = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..', 'PowerPoint_Generator', 'pdf-summarizer', 'ppt_jsons', 'SOFTWARE ENGINEERING', 'chapter_3.json'
        )
    )

    scripts = read_scripts_from_json(json_file)

    if scripts:
        for i, script in enumerate(scripts, start=1):
            print(f"🎙️ Converting script for slide {i} to speech: {script}")
            speak_text(script)
    else:
        print("❌ No scripts found in the JSON file.")