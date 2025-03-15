import requests

API_KEY = "sk_04e26bb82e8c944ad87f77521505173d3b67580619a7a111"  # Replace with your actual API key

url = "https://api.elevenlabs.io/v1/voices"
headers = {"xi-api-key": API_KEY}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    voices = response.json()
    print("Available Voices:")
    for voice in voices["voices"]:
        print(f"- {voice['name']} (ID: {voice['voice_id']})")
else:
    print("Error:", response.json())
