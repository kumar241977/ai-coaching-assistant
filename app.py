from flask import Flask, render_template, request, jsonify
import sqlite3
import uuid
from datetime import datetime
import json
import os

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

def get_ai_coaching_response(user_message, conversation_history, topic):
    """Generate AI-powered adaptive coaching response"""
    try:
        # Try to import OpenAI
        import openai
        
        # Set API key from environment variable
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        if not openai.api_key:
            print("⚠️ No OpenAI API key found, using enhanced fallback")
            return get_enhanced_fallback_response(user_message, conversation_history, topic)
        
        # Build conversation context
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

The client is working on: {topic}

Conversation style:
- Warm, professional, supportive
- Ask 1-2 powerful questions per response
- Acknowledge emotions and patterns
- Help connect insights to actions
- Use "I notice..." and "What do you think..." language

Current conversation depth: {len(conversation_history)} exchanges"""
            }
        ]
        
        # Add conversation history for context
        for entry in conversation_history[-6:]:  # Last 6 messages for context
            role = "assistant" if entry['role'] == 'coach' else "user"
            messages.append({"role": role, "content": entry['content']})
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        print(f"🤖 AI DEBUG: Making OpenAI request with {len(messages)} messages")
        
        # Make OpenAI request with timeout protection
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,  # Reduced for faster response
                temperature=0.7,
                timeout=5  # Shorter timeout
            )
        except Exception as openai_error:
            print(f"❌ AI DEBUG: OpenAI request failed: {openai_error}")
            # Immediately fall back to enhanced responses
            raise openai_error
        
        ai_message = response.choices[0].message.content.strip()
        
        # Extract questions from the response (simple heuristic)
        lines = ai_message.split('\n')
        questions = [line.strip('- ').strip() for line in lines if '?' in line][-2:]  # Last 2 questions
        
        # If no questions found, generate some
        if not questions:
            questions = [
                "What patterns are you noticing as we explore this?",
                "What feels most important for you to understand about this situation?"
            ]
        
        print(f"✅ AI DEBUG: OpenAI response generated successfully")
        return {
            'message': ai_message,
            'questions': questions,
            'ai_powered': True
        }
        
    except ImportError:
        print("⚠️ OpenAI not available, using enhanced fallback")
        return get_enhanced_fallback_response(user_message, conversation_history, topic)
    except Exception as e:
        print(f"❌ AI DEBUG: OpenAI error: {e}")
        return get_enhanced_fallback_response(user_message, conversation_history, topic)

def get_enhanced_fallback_response(user_message, conversation_history, topic):
    """Enhanced fallback with conversation context awareness"""
    user_lower = user_message.lower()
    conversation_depth = len(conversation_history)
    
    # Analyze previous conversation for context
    previous_topics = []
    for entry in conversation_history[-3:]:  # Last 3 messages
        content = entry['content'].lower()
        if 'fear' in content or 'scared' in content:
            previous_topics.append('fear')
        if 'stress' in content or 'anxiety' in content:
            previous_topics.append('stress')
        if 'confidence' in content:
            previous_topics.append('confidence')
    
    # Enhanced keyword detection - works at any conversation depth
    
    # Procrastination responses (any depth)
    if any(word in user_lower for word in ['procrastination', 'procrastinate', 'putting off', 'delay', 'avoiding', 'struggle']):
        if conversation_depth <= 2:
            return {
                'message': "I hear that procrastination is showing up as a significant challenge for you. That takes courage to name directly. What do you notice about when procrastination tends to happen most for you?",
                'questions': [
                    "What tasks do you find yourself putting off most often?",
                    "What might be underneath the procrastination - fear, perfectionism, or something else?"
                ]
            }
        else:
            context_text = f" building on what we've discussed about {', '.join(set(previous_topics))}" if previous_topics else ""
            return {
                'message': f"I'm hearing procrastination come up again in our conversation{context_text}. What patterns are you noticing about when this avoidance shows up most strongly?",
                'questions': [
                    "What would need to feel different for you to approach these tasks directly?",
                    "What's the cost of this procrastination pattern on your confidence and well-being?"
                ]
            }
    
    # Fear and failure responses (any depth)
    elif any(word in user_lower for word in ['fear', 'scared', 'afraid', 'failure', 'fail', 'worried']):
        if 'fear' in previous_topics:
            return {
                'message': "I'm noticing fear has come up multiple times in our conversation. This suggests it's playing a central role in your experience. What do you think this fear is ultimately trying to protect you from?",
                'questions': [
                    "If this fear wasn't present, what would you do differently?",
                    "What would you need to feel more equipped to handle potential failure?"
                ]
            }
        else:
            return {
                'message': "I can hear that fear is playing a significant role in your experience. Fear of failure is incredibly common, and it takes real courage to name it. What do you think this fear is trying to protect you from?",
                'questions': [
                    "When you imagine completing the task successfully, what comes up for you?",
                    "What would it mean about you if you did fail at this task?"
                ]
            }
    
    # Physical symptoms and body responses
    elif any(word in user_lower for word in ['body', 'shiver', 'sweat', 'profusely', 'physical', 'symptoms']):
        context_text = f" I'm also noticing this connects to the {' and '.join(set(previous_topics))} we discussed earlier." if previous_topics else ""
        return {
            'message': f"I can hear how intensely your body is responding to these challenging situations.{context_text} Your body is giving you important information about your stress response. What do you think your body is trying to tell you?",
            'questions': [
                "What helps you feel more grounded when you notice these physical reactions?",
                "What would it be like to approach a challenging task when your body feels calm and ready?"
            ]
        }
    
    # Self-doubt and belief responses
    elif any(word in user_lower for word in ['believe', 'not be able', 'cannot', 'reasons', 'make excuses', 'doubt']):
        context_text = f" given everything we've explored about {' and '.join(set(previous_topics))}" if previous_topics else ""
        return {
            'message': f"I hear you describing the internal narrative that emerges{context_text}. It sounds like there's a part of you that creates reasons to step away from the challenge. What do you think that part is trying to protect you from?",
            'questions': [
                "What would you tell a close friend who shared this same internal dialogue with you?",
                "What evidence do you have that contradicts this 'not being able' belief?"
            ]
        }
    
    # Confidence and self-worth responses  
    elif any(word in user_lower for word in ['confidence', 'self-confidence', 'doubt', 'self-doubt', 'losing', 'loosing']):
        return {
            'message': f"Given everything we've explored - from {', '.join(set(previous_topics))} to now discussing confidence - I'm curious what insights are emerging for you. What's becoming clearer about your relationship with these challenging tasks?",
            'questions': [
                "What would be one small step that could help you build evidence of your capability?",
                "How might you apply what you're learning here to future situations?"
            ]
        }
    
    # Enhanced adaptive responses with context
    if any(word in user_lower for word in ['stress', 'stressed', 'anxiety', 'anxious', 'overwhelm', 'overwhelmed']):
        context_text = " I'm also noticing this connects to the fear we discussed earlier." if 'fear' in previous_topics else ""
        return {
            'message': f"I can sense the weight of stress and anxiety you're carrying.{context_text} What do you notice happens in your body when you think about these complex tasks?",
            'questions': [
                "What would it feel like to approach these tasks from a place of calm rather than stress?",
                "What support or resources might help you manage this anxiety?"
            ]
        }
    
    # Default with conversation awareness
    theme_text = f" building on what we've discussed about {' and '.join(set(previous_topics))}" if previous_topics else ""
    return {
        'message': f"I can hear the depth of what you're sharing{theme_text}. What feels most significant to you right now?",
        'questions': [
            "What patterns are you noticing as we talk about this?",
            "What would you most like to understand or change about this situation?"
        ]
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start-session', methods=['POST'])
def start_session():
    """Start a new coaching session - AI POWERED VERSION"""
    try:
        print(f"🔍 AI START_SESSION: Starting new session...")
        
        user_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        
        print(f"🔍 AI START_SESSION: user_id={user_id}, session_id={session_id}")
        
        # Store in memory with conversation history
        sessions[session_id] = {
            'user_id': user_id,
            'session_id': session_id,
            'stage': 'intake',
            'topic': None,
            'conversation_history': [],
            'created_at': datetime.now().isoformat()
        }
        
        # Simple response
        response = {
            'message': 'Welcome to your coaching session! I\'m here to support you in exploring what\'s important to you. This is a confidential space where you can share openly.',
            'questions': [
                'What brings you to coaching right now?',
                'What would you like to explore in this session?', 
                'How can I best support you today?'
            ],
            'stage': 'intake',
            'available_topics': ['performance_improvement', 'career_development', 'work_life_balance', 'leadership_growth']
        }
        
        print(f"✅ AI START_SESSION: Session created successfully")
        return jsonify({
            'session_id': session_id,
            'user_id': user_id,
            'response': response
        })
        
    except Exception as e:
        print(f"❌ AI START_SESSION: Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Failed to start session: {str(e)}'}), 500

@app.route('/api/send-message', methods=['POST'])
def send_message():
    """Process user message - AI ADAPTIVE VERSION"""
    try:
        print(f"🔍 AI SEND_MESSAGE: Starting...")
        
        data = request.json
        session_id = data.get('session_id')
        user_message = data.get('message')
        message_type = data.get('type', 'text')
        
        print(f"🔍 AI SEND_MESSAGE: session_id={session_id}, message='{user_message}', type={message_type}")
        
        if not session_id or not user_message:
            return jsonify({'error': 'Missing session_id or message'}), 400
        
        # Check if session exists
        if session_id not in sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        session = sessions[session_id]
        
        # Add user message to conversation history
        session['conversation_history'].append({
            'role': 'user',
            'content': user_message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Process different message types
        if message_type == 'topic_selection':
            print(f"🔍 AI SEND_MESSAGE: Processing topic selection: {user_message}")
            
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
            session['topic'] = user_message
            session['stage'] = 'exploration'
            
        else:
            # Use AI-powered adaptive response
            print(f"🔍 AI SEND_MESSAGE: Generating AI response...")
            
            topic = session.get('topic', 'performance improvement')
            conversation_history = session.get('conversation_history', [])
            
            response = get_ai_coaching_response(user_message, conversation_history, topic)
            print(f"🔍 AI SEND_MESSAGE: AI response generated: {response.get('ai_powered', False)}")
        
        # Add coach response to history
        session['conversation_history'].append({
            'role': 'coach',
            'content': response['message'],
            'timestamp': datetime.now().isoformat()
        })
        
        # Update response with standard fields
        response.update({
            'stage': 'exploration',
            'competency_applied': 'active_listening',
            'ai_confidence': 0.9,
            'demo_mode': True,
            'emotional_analysis': {'primary_emotion': 'engaged', 'intensity': 0.7}
        })
        
        print(f"✅ AI SEND_MESSAGE: Response generated successfully")
        return jsonify(response)
        
    except Exception as e:
        print(f"❌ AI SEND_MESSAGE: Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

if __name__ == '__main__':
    print("🚀 Starting AI-powered adaptive coaching app...")
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True) 
