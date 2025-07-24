from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
from datetime import datetime
import uuid
from conversation_flow import ConversationFlowEngine, ConversationStage
from nlp_personalization import EmotionalToneAnalyzer, PersonalizationEngine
import sqlite3
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'coaching-assistant-secret-key-2024')
CORS(app)

# Initialize core components
conversation_engine = ConversationFlowEngine()
tone_analyzer = EmotionalToneAnalyzer()
personalization_engine = PersonalizationEngine()

# Database setup
def init_db():
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
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            preferences TEXT,
            communication_style TEXT,
            created_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start-session', methods=['POST'])
def start_session():
    """Start a new coaching session"""
    user_id = request.json.get('user_id', str(uuid.uuid4()))
    session_id = str(uuid.uuid4())
    
    # Create new conversation state
    state = conversation_engine.start_new_session(user_id, session_id)
    
    # Generate initial intake response
    response = conversation_engine.generate_intake_response(state)
    
    # Store session in database
    save_session_to_db(state)
    
    return jsonify({
        'session_id': session_id,
        'user_id': user_id,
        'response': response
    })

@app.route('/api/send-message', methods=['POST'])
def send_message():
    """Process user message and generate coaching response"""
    data = request.json
    session_id = data.get('session_id')
    user_message = data.get('message')
    message_type = data.get('type', 'text')  # text, topic_selection, action_commitment
    
    if not session_id or not user_message:
        return jsonify({'error': 'Missing session_id or message'}), 400
    
    # Get conversation state
    state = conversation_engine.get_session(session_id)
    if not state:
        return jsonify({'error': 'Session not found'}), 404
    
    # Analyze emotional tone
    emotional_analysis = tone_analyzer.analyze_tone(user_message)
    
    # Generate response based on current stage and message type
    if message_type == 'topic_selection':
        response = conversation_engine.process_topic_selection(state, user_message)
    elif message_type == 'action_commitment':
        action_data = json.loads(user_message) if isinstance(user_message, str) else user_message
        response = conversation_engine.process_action_commitment(state, action_data)
    else:
        # Regular conversation flow
        if state.current_stage == ConversationStage.INTAKE:
            response = conversation_engine.generate_intake_response(state)
        elif state.current_stage == ConversationStage.EXPLORATION:
            response = conversation_engine.generate_exploration_response(state, user_message)
        elif state.current_stage == ConversationStage.REFLECTION:
            response = conversation_engine.generate_reflection_response(state, user_message)
        elif state.current_stage == ConversationStage.ACTION_PLANNING:
            response = conversation_engine.generate_action_planning_response(state, user_message)
        else:
            response = {'error': 'Invalid conversation stage'}
    
    # Personalize response based on emotional tone and user preferences
    if 'error' not in response:
        personalized_response = personalization_engine.personalize_response(
            response, emotional_analysis, state.user_id
        )
        response.update(personalized_response)
    
    # Save updated session
    save_session_to_db(state)
    
    # Add emotional analysis to response
    response['emotional_analysis'] = emotional_analysis
    
    return jsonify(response)

@app.route('/api/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """Get session details"""
    state = conversation_engine.get_session(session_id)
    if not state:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({
        'session_id': state.session_id,
        'user_id': state.user_id,
        'current_stage': state.current_stage.value,
        'topic': state.topic.name if state.topic else None,
        'conversation_history': state.conversation_history,
        'insights': state.insights,
        'actions': state.actions,
        'created_at': state.created_at.isoformat(),
        'updated_at': state.updated_at.isoformat()
    })

@app.route('/api/sessions/<user_id>', methods=['GET'])
def get_user_sessions(user_id):
    """Get all sessions for a user"""
    conn = sqlite3.connect('coaching_sessions.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, topic, current_stage, created_at, updated_at 
        FROM sessions 
        WHERE user_id = ?
        ORDER BY updated_at DESC
    ''', (user_id,))
    
    sessions = []
    for row in cursor.fetchall():
        sessions.append({
            'session_id': row[0],
            'topic': row[1],
            'current_stage': row[2],
            'created_at': row[3],
            'updated_at': row[4]
        })
    
    conn.close()
    return jsonify({'sessions': sessions})

@app.route('/api/stage-transition', methods=['POST'])
def stage_transition():
    """Manually transition conversation stage"""
    data = request.json
    session_id = data.get('session_id')
    new_stage = data.get('stage')
    
    state = conversation_engine.get_session(session_id)
    if not state:
        return jsonify({'error': 'Session not found'}), 404
    
    try:
        state.current_stage = ConversationStage(new_stage)
        state.updated_at = datetime.now()
        save_session_to_db(state)
        
        return jsonify({'success': True, 'new_stage': new_stage})
    except ValueError:
        return jsonify({'error': 'Invalid stage'}), 400

def save_session_to_db(state):
    """Save conversation state to database"""
    conn = sqlite3.connect('coaching_sessions.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO sessions 
        (id, user_id, topic, current_stage, conversation_history, insights, actions, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        state.session_id,
        state.user_id,
        state.topic.name if state.topic else None,
        state.current_stage.value,
        json.dumps(state.conversation_history),
        json.dumps(state.insights),
        json.dumps(state.actions),
        state.created_at.isoformat(),
        state.updated_at.isoformat()
    ))
    
    conn.commit()
    conn.close()

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
