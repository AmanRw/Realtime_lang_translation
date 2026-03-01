from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from deep_translator import GoogleTranslator
import uvicorn

app = FastAPI()
translator = GoogleTranslator(source='auto', target='hindi')

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("Client connected via FastAPI WebSocket")
    try:
        while True:
            # Receive text from client
            data = await websocket.receive_text()
            
            # Translate
            translated_text = translator.translate(data)
            print(f"Original: {data} -> Translated: {translated_text}")
            
            # Send back the translated text
            await websocket.send_text(translated_text)
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
