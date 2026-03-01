# 🌍 Multilingual Real-Time Chat Application

A web-based real-time chat application with automatic language translation built using Flask, Flask-SocketIO, and modern web technologies.

## Features

- ✅ **Room Creation & Joining**: Create rooms with unique codes or join existing rooms
- ✅ **Real-Time Messaging**: WebSocket-based instant messaging
- ✅ **Automatic Translation**: Messages are automatically translated to each user's preferred language
- ✅ **Language Selection**: Support for 10+ languages (English, Hindi, French, Spanish, German, Japanese, Chinese, Arabic, Portuguese, Russian)
- ✅ **Modern UI**: Clean, responsive design with smooth animations
- ✅ **Connection Status**: Real-time connection status indicator

## Technology Stack

### Backend
- **Flask**: Web framework
- **Flask-SocketIO**: WebSocket support for real-time communication
- **deep-translator**: Google Translate API integration
- **langdetect**: Automatic language detection

### Frontend
- **HTML5/CSS3**: Modern, responsive UI
- **JavaScript**: Client-side logic
- **Socket.IO Client**: WebSocket communication

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or download the project**
   ```bash
   cd project
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Start the Flask server**
   ```bash
   python app.py
   ```

2. **Open your browser**
   - Navigate to `http://localhost:5000`
   - The application will be running on port 5000

3. **Test the application**
   - Open the URL in two different browser windows/tabs
   - Create a room in one window
   - Join the room using the code in the other window
   - Select different languages for each user
   - Start chatting and see messages auto-translate!

## Usage Guide

### Creating a Room

1. Enter your name in the "Your Name" field
2. Click "Create Room"
3. You'll be redirected to the language selection page
4. Select your preferred language
5. Start chatting!

### Joining a Room

1. Enter your name in the "Your Name" field
2. Enter the 6-character room code
3. Click "Join Room"
4. Select your preferred language
5. Start chatting!

### Chatting

- Type your message in the input box at the bottom
- Press Enter or click Send
- Your message will be automatically translated to each recipient's language
- Messages appear in real-time with timestamps

## Project Structure

```
project/
├── app.py                 # Flask backend with SocketIO
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── templates/
│   ├── index.html        # Landing page
│   └── chat.html         # Chat interface
└── static/
    └── style.css         # Stylesheet
```

## Demo Constraints

For stability and demo purposes, the application has the following constraints:

- **Maximum 1 active room** at a time
- **Maximum 2 users** per room
- **No persistent storage** (rooms are stored in memory)
- **No authentication** required

These constraints can be easily modified in the code for production use.

## Supported Languages

- English (en)
- Hindi (hi)
- French (fr)
- Spanish (es)
- German (de)
- Japanese (ja)
- Chinese (zh)
- Arabic (ar)
- Portuguese (pt)
- Russian (ru)

## How Translation Works

1. User A sends a message in their language
2. Server detects the source language using `langdetect`
3. For each recipient (including sender), the message is translated to their preferred language using `deep-translator`
4. Each user receives the message in their selected language

## Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify the port in `app.py`:
```python
socketio.run(app, debug=True, host='0.0.0.0', port=5001)  # Change port number
```

### Translation Errors
If translation fails, the original message will be displayed. This can happen due to:
- Network issues
- Unsupported language combinations
- API rate limits

### Connection Issues
- Ensure the Flask server is running
- Check browser console for errors
- Verify WebSocket support in your browser

## Future Enhancements

Potential improvements for production use:

- [ ] Multi-room support
- [ ] User authentication
- [ ] Message history/persistence
- [ ] File sharing
- [ ] Voice messages
- [ ] Emoji support
- [ ] User profiles
- [ ] Room password protection
- [ ] Admin controls

## License

This project is created for hackathon

**Enjoy chatting in multiple languages! 🌍💬**
