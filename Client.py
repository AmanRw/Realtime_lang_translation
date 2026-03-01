import asyncio
import websockets
import speech_recognition as sr
from gtts import gTTS
import pygame
import io

# Initialize Audio Mixer for TTS playback
pygame.mixer.init()

def speak_text(text, lang='es'):
    """Converts text to speech and plays it immediately."""
    tts = gTTS(text=text, lang=lang)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    pygame.mixer.music.load(fp)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        continue

async def stream_audio():
    # FastAPI default WebSocket URL
    uri = "ws://localhost:8000/ws"
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    try:
        async with websockets.connect(uri) as websocket:
            print("Connected to FastAPI. Speak now...")
            while True:
                with mic as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    try:
                        print("Listening...")
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        
                        # STT: Voice to Text (Local)
                        text = recognizer.recognize_google(audio) # type: ignore
                        print(f"You: {text}")

                        # Send to FastAPI
                        await websocket.send(text)

                        # Get Translation from FastAPI
                        translation = await websocket.recv()
                        print(f"Translator: {translation}")

                        # TTS: Speak the translation
                        speak_text(translation)

                    except Exception as e:
                        print(f"Retry: {e}")
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    asyncio.run(stream_audio())
