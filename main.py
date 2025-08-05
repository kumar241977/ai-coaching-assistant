from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import uuid
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure OpenAI API key
openai_api_key = os.getenv('OPENAI_API_KEY')

# Simple in-memory storage for sessions
sessions = {}

@app.route('/')
def index():
    """Serve the main application page"""
    return render_template('index.html')

@app.route('/api/start-session', methods=['POST'])
def start_session():
    """Start a new coaching session"""
    try:
        print("🔍 Starting new session...")
        
        user_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        
        # Store session in memory
        sessions[session_id] = {
            'user_id': user_id,
            'session_id': session_id,
            'stage': 'intake',
            'topic': None,
            'conversation_history': [],
            'created_at': datetime.now().isoformat()
        }
        
        print(f"✅ Session created: {session_id}")
        
        return jsonify({
            'session_id': session_id,
            'user_id': user_id
        })
        
    except Exception as e:
        print(f"❌ Session creation error: {e}")
        return jsonify({'error': 'Failed to start session'}), 500

@app.route('/api/send-message', methods=['POST'])
def send_message():
    """Process user message and return AI coaching response"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        user_message = data.get('message', '')
        message_type = data.get('type', 'text')
        
        print(f"🔍 Processing message: {user_message}")
        
        if not session_id or session_id not in sessions:
            return jsonify({'error': 'Invalid session'}), 400
        
        session = sessions[session_id]
        
        # Add user message to history
        session['conversation_history'].append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Handle topic selection
        if message_type == 'topic_selection':
            session['topic'] = user_message
            response = get_topic_response(user_message)
        else:
            # Generate AI coaching response
            response = get_ai_coaching_response(user_message, session['conversation_history'], session.get('topic', 'general'))
        
        # Add coach response to history
        session['conversation_history'].append({
            'role': 'coach',
            'content': response['message'],
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"✅ Response generated successfully")
        
        return jsonify({
            'message': response['message'],
            'questions': response.get('questions', []),
            'stage': 'exploration',
            'competency_applied': 'active_listening',
            'ai_confidence': 0.9,
            'demo_mode': not response.get('ai_powered', False),
            'emotional_analysis': {'primary_emotion': 'engaged', 'intensity': 0.7}
        })
        
    except Exception as e:
        print(f"❌ Message processing error: {e}")
        return jsonify({'error': 'Failed to process message'}), 500

def get_topic_response(topic):
    """Get initial response for selected topic"""
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
    
    return topic_responses.get(topic, {
        'message': f"Thank you for selecting {topic}. Let's explore this together.",
        'questions': ["What would you like to focus on first?", "What's most important to you about this topic?"]
    })

def get_ai_coaching_response(user_message, conversation_history, topic):
    """Generate AI-powered coaching response or fallback"""
    
    # Try OpenAI API if available
    if openai_api_key:
        try:
            response = call_openai_api(user_message, conversation_history, topic)
            if response:
                return {
                    'message': response,
                    'questions': ["What patterns are you noticing?", "What feels most important to explore?"],
                    'ai_powered': True
                }
        except Exception as e:
            print(f"❌ OpenAI API failed: {e}")
    
    # Fallback to intelligent responses
    return get_intelligent_fallback_response(user_message, conversation_history, topic)

def call_openai_api(user_message, conversation_history, topic):
    """Call OpenAI API directly via HTTP"""
    try:
        headers = {
            'Authorization': f'Bearer {openai_api_key}',
            'Content-Type': 'application/json'
        }
        
        messages = [
            {
                "role": "system",
                "content": f"""You are an expert ICF-certified executive coach specializing in {topic}. 
                
Key coaching principles:
- Use powerful questions to create awareness
- Listen actively and reflect what you hear
- Help the client discover their own insights
- Focus on action and accountability
- Be empathetic but challenge thinking patterns
- Never give direct advice - guide discovery

Conversation style:
- Warm, professional, supportive
- Ask 1-2 powerful questions per response
- Acknowledge emotions and patterns
- Help connect insights to actions"""
            }
        ]
        
        # Add recent conversation history
        for entry in conversation_history[-4:]:
            role = "assistant" if entry['role'] == 'coach' else "user"
            messages.append({"role": role, "content": entry['content']})
        
        messages.append({"role": "user", "content": user_message})
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': messages,
            'max_tokens': 200,
            'temperature': 0.7
        }
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=15
        )
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            print(f"❌ OpenAI API error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ OpenAI API call failed: {e}")
        return None

def get_intelligent_fallback_response(user_message, conversation_history, topic):
    """Intelligent fallback responses based on user input"""
    user_lower = user_message.lower()
    
    # Procrastination responses
    if any(word in user_lower for word in ['procrastination', 'procrastinate', 'putting off', 'delay', 'avoiding']):
        return {
            'message': "I hear that procrastination is showing up as a significant challenge for you. That takes courage to name directly. What do you notice about when procrastination tends to happen most for you?",
            'questions': [
                "What tasks do you find yourself putting off most often?",
                "What might be underneath the procrastination - fear, perfectionism, or something else?"
            ]
        }
    
    # Fear and failure responses
    elif any(word in user_lower for word in ['fear', 'scared', 'afraid', 'failure', 'fail', 'worried']):
        return {
            'message': "I can hear that fear is playing a significant role in your experience. Fear of failure is incredibly common, and it takes real courage to name it. What do you think this fear is trying to protect you from?",
            'questions': [
                "When you imagine completing the task successfully, what comes up for you?",
                "What would it mean about you if you did fail at this task?"
            ]
        }
    
    # Stress and overwhelm responses
    elif any(word in user_lower for word in ['stress', 'overwhelm', 'too much', 'pressure', 'anxiety']):
        return {
            'message': "It sounds like you're carrying quite a bit right now. Stress and feeling overwhelmed can really impact our ability to perform at our best. What would it feel like to have more space and clarity?",
            'questions': [
                "What would need to change for you to feel more in control?",
                "If you could delegate or eliminate one thing, what would it be?"
            ]
        }
    
    # Default thoughtful response
    else:
        return {
            'message': "Thank you for sharing that with me. I can hear that this is important to you. What feels most significant about what you just shared?",
            'questions': [
                "What patterns are you noticing as we explore this?",
                "What would you most like to understand about this situation?"
            ]
        }

if __name__ == '__main__':
    print("🚀 Starting AI Coaching Assistant...")
    app.run(host='0.0.0.0', port=5000, debug=True) 