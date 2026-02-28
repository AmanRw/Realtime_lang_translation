import asyncio
import websockets
import speech_recognition as sr
import sys

async def stream_audio():
    uri = "ws://localhost:8765"
    
    # 1. Initialize Microphone and Recognizer
    recognizer = sr.Recognizer()
    
    # Diagnostic: Check if the method exists at runtime
    if not hasattr(recognizer, 'recognize_google'):
        print("Error: recognize_google method not found. Check your installation.")
        return

    try:
        mic = sr.Microphone()
    except OSError:
        print("Error: No microphone found. Check your hardware/drivers.")
        return

    # 2. Connect to the WebSocket Server
    try:
        async with websockets.connect(uri) as websocket:
            print("Successfully connected to Server.")
            print(">>> START SPEAKING NOW...")
            
            while True:
                with mic as source:
                    # Adjust for ambient noise to improve accuracy
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    try:
                        print("Listening (5s window)...")
                        # Capture audio (timeout stops it from waiting forever)
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        
                        # 3. Convert Voice to Text
                        # Using 'type: ignore' to silence VS Code warnings
                        text = recognizer.recognize_google(audio) # type: ignore
                        print(f"You said: {text}")

                        # 4. Send to Server & Wait for Translation
                        await websocket.send(text)
                        translation = await websocket.recv()
                        
                        print(f"--- Translation: {translation} ---\n")

                    except sr.WaitTimeoutError:
                        print("No speech detected, still listening...")
                    except sr.UnknownValueError:
                        print("Could not understand audio. Try again.")
                    except sr.RequestError as e:
                        print(f"Could not request results from Google; {e}")
                    except Exception as e:
                        print(f"Loop Error: {e}")

    except ConnectionRefusedError:
        print("Error: Server is not running. Start server.py first!")
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(stream_audio())
    except KeyboardInterrupt:
        print("\nClient stopped by user.")
        sys.exit()
