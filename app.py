from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import random
import string
from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException
import json
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory room storage
rooms = {}

# Supported languages
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'Hindi',
    'fr': 'French',
    'es': 'Spanish',
    'de': 'German',
    'ja': 'Japanese',
    'zh': 'Chinese',
    'ar': 'Arabic',
    'pt': 'Portuguese',
    'ru': 'Russian'
}

def generate_room_code():
    """Generate a random 6-character room code"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def get_room_by_code(room_code):
    """Get room by code, return None if not found"""
    return rooms.get(room_code.upper())

def create_room():
    """Create a new room and return its code"""
    room_code = generate_room_code()
    rooms[room_code] = {
        'users': {},
        'created_at': datetime.now().isoformat()
    }
    return room_code

def add_user_to_room(room_code, socket_id, username, language):
    """Add user to room"""
    room = get_room_by_code(room_code)
    if room:
        room['users'][socket_id] = {
            'username': username,
            'language': language
        }
        return True
    return False

def remove_user_from_room(room_code, socket_id):
    """Remove user from room"""
    room = get_room_by_code(room_code)
    if room and socket_id in room['users']:
        del room['users'][socket_id]
        # Auto-delete room if empty
        if len(room['users']) == 0:
            del rooms[room_code]
        return True
    return False

def translate_message(message, target_language, source_language=None):
    """Translate message to target language"""
    try:
        if source_language and source_language == target_language:
            return message
        
        translator = GoogleTranslator(source=source_language or 'auto', target=target_language)
        translated = translator.translate(message)
        return translated
    except Exception as e:
        print(f"Translation error: {e}")
        return message  # Return original if translation fails

def detect_message_language(message):
    """Detect the language of a message"""
    try:
        detected = detect(message)
        return detected
    except LangDetectException:
        return 'en'  # Default to English if detection fails

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/chat')
def chat():
    """Chat page"""
    return render_template('chat.html')

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {request.sid}")
    emit('connected', {'status': 'success'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")
    # Find and remove user from any room
    for room_code, room in list(rooms.items()):
        if request.sid in room['users']:
            username = room['users'][request.sid].get('username', 'Unknown')
            remove_user_from_room(room_code, request.sid)
            leave_room(room_code)
            # Notify other users
            emit('user_left', {'username': username}, room=room_code, skip_sid=request.sid)
            break

@socketio.on('create_room')
def handle_create_room(data):
    """Handle room creation"""
    try:
        username = data.get('username', 'User').strip()
        if not username:
            emit('error', {'message': 'Username is required'})
            return
        
        # Check if there's already an active room (demo constraint: max 1 room)
        if len(rooms) >= 1:
            # Find existing room
            existing_room_code = list(rooms.keys())[0]
            existing_room = rooms[existing_room_code]
            if len(existing_room['users']) >= 2:
                emit('error', {'message': 'Maximum rooms reached. Please join existing room.'})
                return
            else:
                # Join existing room if it has space
                room_code = existing_room_code
        else:
            # Create new room
            room_code = create_room()
        
        # Add user to room (will be completed after language selection)
        join_room(room_code)
        emit('room_created', {
            'room_code': room_code,
            'message': 'Room created successfully'
        })
    except Exception as e:
        print(f"Error creating room: {e}")
        emit('error', {'message': 'Failed to create room'})

@socketio.on('join_room')
def handle_join_room(data):
    """Handle room joining"""
    try:
        room_code = data.get('room_code', '').strip().upper()
        username = data.get('username', 'User').strip()
        
        if not room_code or not username:
            emit('error', {'message': 'Room code and username are required'})
            return
        
        room = get_room_by_code(room_code)
        if not room:
            emit('error', {'message': 'Room not found. Please check the room code.'})
            return
        
        # Check room capacity (demo constraint: max 2 users)
        if len(room['users']) >= 2:
            emit('error', {'message': 'Room is full. Maximum 2 users allowed.'})
            return
        
        # Check if user is already in room
        if request.sid in room['users']:
            emit('error', {'message': 'You are already in this room'})
            return
        
        join_room(room_code)
        emit('room_joined', {
            'room_code': room_code,
            'message': 'Joined room successfully'
        })
    except Exception as e:
        print(f"Error joining room: {e}")
        emit('error', {'message': 'Failed to join room'})

@socketio.on('set_language')
def handle_set_language(data):
    """Handle language selection and finalize user join"""
    try:
        room_code = data.get('room_code', '').strip().upper()
        username = data.get('username', 'User').strip()
        language = data.get('language', 'en').strip()
        
        if not room_code or not username:
            emit('error', {'message': 'Room code and username are required'})
            return
        
        if language not in SUPPORTED_LANGUAGES:
            emit('error', {'message': 'Unsupported language'})
            return
        
        room = get_room_by_code(room_code)
        if not room:
            emit('error', {'message': 'Room not found'})
            return
        
        # Check room capacity
        if len(room['users']) >= 2 and request.sid not in room['users']:
            emit('error', {'message': 'Room is full'})
            return
        
        # Add/update user in room
        if add_user_to_room(room_code, request.sid, username, language):
            # Notify other users
            emit('user_joined', {
                'username': username,
                'language': SUPPORTED_LANGUAGES.get(language, language),
                'user_count': len(room['users'])
            }, room=room_code, skip_sid=request.sid)
            
            # Send confirmation to user
            emit('language_set', {
                'status': 'success',
                'username': username,
                'language': language,
                'room_code': room_code,
                'user_count': len(room['users'])
            })
        else:
            emit('error', {'message': 'Failed to join room'})
    except Exception as e:
        print(f"Error setting language: {e}")
        emit('error', {'message': 'Failed to set language'})

@socketio.on('send_message')
def handle_send_message(data):
    """Handle message sending and translation"""
    try:
        room_code = data.get('room_code', '').strip().upper()
        message = data.get('message', '').strip()
        
        if not room_code or not message:
            emit('error', {'message': 'Room code and message are required'})
            return
        
        room = get_room_by_code(room_code)
        if not room:
            emit('error', {'message': 'Room not found'})
            return
        
        if request.sid not in room['users']:
            emit('error', {'message': 'You are not in this room'})
            return
        
        sender = room['users'][request.sid]
        username = sender['username']
        
        # Detect source language
        source_language = detect_message_language(message)
        
        # Get current timestamp
        timestamp = datetime.now().strftime('%H:%M')
        
        # Translate and send to each user in the room
        for socket_id, user_info in room['users'].items():
            target_language = user_info['language']
            
            # Translate message for this user
            translated_message = translate_message(
                message,
                target_language,
                source_language if source_language != target_language else None
            )
            
            # Send translated message
            emit('receive_message', {
                'from': username,
                'message': translated_message,
                'original_message': message if socket_id == request.sid else None,  # Show original to sender
                'timestamp': timestamp,
                'language': SUPPORTED_LANGUAGES.get(target_language, target_language)
            }, room=socket_id)
        
    except Exception as e:
        print(f"Error sending message: {e}")
        emit('error', {'message': 'Failed to send message'})

if __name__ == '__main__':
    print("Starting Flask-SocketIO server...")
    print("Open http://localhost:5000 in your browser")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
