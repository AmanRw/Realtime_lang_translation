import asyncio
import websockets
from deep_translator import GoogleTranslator

# Initialize translator globally
translator = GoogleTranslator(source='auto', target='es')

async def translate_handler(websocket):
    print(f"--- Client Connected ---")
    try:
        async for message in websocket:
            # message is the text received from the client's STT
            translated_text = translator.translate(message)
            
            print(f"Received: {message} -> Sent: {translated_text}")
            await websocket.send(translated_text)
    except websockets.exceptions.ConnectionClosed:
        print("--- Client Disconnected ---")

async def main():
    async with websockets.serve(translate_handler, "localhost", 8765):
        print("Server running on ws://localhost:8765")
        await asyncio.Future()  # Keep server running

if __name__ == "__main__":
    asyncio.run(main())
