from flask import Flask, render_template, request, jsonify
import sqlite3
import uuid
from datetime import datetime
import json

app = Flask(__name__)

# Simple in-memory storage for testing
sessions = {}

def init_db():
    """Initialize database"""
    try:
        conn = sqlite3.connect('coaching_sessions.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                topic TEXT,
                current_stage TEXT,
                conversation_history TEXT,
                insights TEXT,
                actions TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start-session', methods=['POST'])
def start_session():
    """Start a new coaching session - MINIMAL VERSION"""
    try:
        print(f"🔍 MINIMAL START_SESSION: Starting new session...")
        
        user_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        
        print(f"🔍 MINIMAL START_SESSION: user_id={user_id}, session_id={session_id}")
        
        # Store in memory for now
        sessions[session_id] = {
            'user_id': user_id,
            'session_id': session_id,
            'stage': 'intake',
            'topic': None,
            'created_at': datetime.now().isoformat()
        }
        
        # Simple response
        response = {
            'message': 'Welcome to your coaching session! What would you like to work on today?',
            'questions': [
                'What brings you to coaching right now?',
                'What would you like to explore in this session?', 
                'How can I best support you today?'
            ],
            'stage': 'intake',
            'available_topics': ['performance_improvement', 'career_development', 'work_life_balance', 'leadership_growth']
        }
        
        print(f"✅ MINIMAL START_SESSION: Session created successfully")
        return jsonify({
            'session_id': session_id,
            'user_id': user_id,
            'response': response
        })
        
    except Exception as e:
        print(f"❌ MINIMAL START_SESSION: Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to start session: {str(e)}'}), 500

@app.route('/api/send-message', methods=['POST'])
def send_message():
    """Process user message - MINIMAL VERSION"""
    try:
        print(f"🔍 MINIMAL SEND_MESSAGE: Starting...")
        
        data = request.json
        session_id = data.get('session_id')
        user_message = data.get('message')
        message_type = data.get('type', 'text')
        
        print(f"🔍 MINIMAL SEND_MESSAGE: session_id={session_id}, message='{user_message}', type={message_type}")
        
        if not session_id or not user_message:
            return jsonify({'error': 'Missing session_id or message'}), 400
        
        # Check if session exists
        if session_id not in sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        # Simple response based on message type
        if message_type == 'topic_selection':
            print(f"🔍 MINIMAL SEND_MESSAGE: Processing topic selection: {user_message}")
            
            topic_responses = {
                'performance_improvement': {
                    'message': "Great! Let's explore Performance Improvement together. I understand you want to enhance your work performance and productivity. What specific aspects of your performance feel most important to address right now?",
                    'questions': [
                        "What specific aspect of your performance would you like to improve?",
                        "What's currently working well in your performance?"
                    ]
                },
                'career_development': {
                    'message': "Excellent! Career Development is such an important area. I'm excited to explore your career aspirations and help you identify the next steps.",
                    'questions': [
                        "Where do you see yourself in your career journey?",
                        "What career aspirations are most important to you?"
                    ]
                },
                'work_life_balance': {
                    'message': "Thank you for choosing Work-Life Balance. Finding harmony between different aspects of life is crucial for well-being.",
                    'questions': [
                        "How would you describe your current work-life balance?",
                        "What areas of your life feel out of balance?"
                    ]
                },
                'leadership_growth': {
                    'message': "Wonderful! Leadership Growth is a powerful area for development. I'm here to support you in discovering your authentic leadership style.",
                    'questions': [
                        "What kind of leader do you want to be?",
                        "What leadership challenges are you currently facing?"
                    ]
                }
            }
            
            response = topic_responses.get(user_message, {
                'message': f"Thank you for selecting {user_message}. Let's explore this together.",
                'questions': ["What would you like to focus on first?", "What's most important to you about this topic?"]
            })
            
            # Update session
            sessions[session_id]['topic'] = user_message
            sessions[session_id]['stage'] = 'exploration'
            
        else:
            # Handle regular conversation
            print(f"🔍 MINIMAL SEND_MESSAGE: Processing regular message")
            
            # Simple keyword-based response
            user_lower = user_message.lower()
            
            if any(word in user_lower for word in ['procrastination', 'procrastinate', 'putting off', 'delay']):
                response = {
                    'message': "I hear that procrastination is showing up as a significant challenge for you. That takes courage to name directly. What do you notice about when procrastination tends to happen most for you?",
                    'questions': [
                        "What tasks do you find yourself putting off most often?",
                        "What might be underneath the procrastination - fear, perfectionism, or something else?"
                    ]
                }
            else:
                response = {
                    'message': f"Thank you for sharing that with me: '{user_message}'. I can sense this is important to you. What stands out most to you as we explore this together?",
                    'questions': [
                        "What patterns are you noticing?",
                        "How has this been affecting other areas of your life?"
                    ]
                }
        
        response.update({
            'stage': 'exploration',
            'competency_applied': 'active_listening',
            'ai_confidence': 0.8,
            'demo_mode': True,
            'emotional_analysis': {'primary_emotion': 'engaged', 'intensity': 0.7}
        })
        
        print(f"✅ MINIMAL SEND_MESSAGE: Response generated successfully")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ MINIMAL SEND_MESSAGE: Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting minimal coaching app...")
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True) 
