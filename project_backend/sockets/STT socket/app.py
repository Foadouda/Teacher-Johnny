import asyncio
import websockets
import whisper
import json
import os
import numpy as np
import io
import soundfile as sf
import wave

# ✅ Load Whisper Model
model = whisper.load_model("base")

# ✅ File to store transcriptions
JSON_FILE = "Student Questions.json"

# ✅ Function to save transcriptions
def save_transcription(text):
    if not os.path.exists(JSON_FILE):
        with open(JSON_FILE, "w") as file:
            json.dump({"transcriptions": []}, file)

    with open(JSON_FILE, "r+") as file:
        data = json.load(file)
        data["transcriptions"].append({"question": text})
        file.seek(0)
        json.dump(data, file, indent=4)

# ✅ WebSocket handler (Processes audio stream)
async def transcribe_stream(websocket, *args):
    print(f"✅ Client connected: {websocket.remote_address}")

    try:
        async for message in websocket:
            print(f"📡 Received audio data: {len(message)} bytes (5s chunk)")

            # ✅ Convert raw PCM bytes into a properly formatted WAV file
            wav_file = "temp_audio.wav"
            with wave.open(wav_file, "wb") as wf:
                wf.setnchannels(1)  # Mono audio
                wf.setsampwidth(2)  # 16-bit PCM
                wf.setframerate(16000)  # Match Whisper's expected sample rate
                wf.writeframes(message)

            # ✅ Load the WAV file with correct format
            audio_data, sample_rate = sf.read(wav_file, dtype="float32")

            # ✅ Improve transcription accuracy with fine-tuned settings
            result = model.transcribe(
                audio_data,
                temperature=0,  # Reduces randomness in transcription
                no_speech_threshold=0.1,  # Detects speech more aggressively
                condition_on_previous_text=False,  # Prevents context influence
                fp16=False  # Full precision for better accuracy
            )
            transcript = result["text"]
            save_transcription(transcript)

            # ✅ Send transcription to client
            await websocket.send(json.dumps({"transcription": transcript}))

    except websockets.exceptions.ConnectionClosed:
        print("❌ Client disconnected.")
    except Exception as e:
        print(f"⚠️ Error: {e}")

# ✅ Start WebSocket server
async def main():
    start_server = await websockets.serve(transcribe_stream, "0.0.0.0", 8000)
    print("🌍 WebSocket server running at ws://0.0.0.0:8000")
    await start_server.wait_closed()  # Keeps the server running

if __name__ == "__main__":
    asyncio.run(main())
