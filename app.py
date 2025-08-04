from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sqlite3
import uuid
from datetime import datetime
import json
import os
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

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
        # Check if OpenAI API key is available
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
        
        # Make OpenAI request with better error handling
        try:
            # Try using the older OpenAI syntax first for compatibility
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,
                temperature=0.7,
                timeout=10
            )
            
            ai_message = response.choices[0].message.content.strip()
            
        except AttributeError:
            # If old syntax fails, try new client syntax
            print("🔄 Trying new OpenAI client syntax...")
            client = openai.OpenAI(api_key=openai.api_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=200,
                temperature=0.7,
                timeout=10
            )
            
            ai_message = response.choices[0].message.content.strip()
            
        except Exception as openai_error:
            print(f"❌ AI DEBUG: OpenAI request failed: {openai_error}")
            # Immediately fall back to enhanced responses
            return get_enhanced_fallback_response(user_message, conversation_history, topic)
        
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
        
    except Exception as e:
        print(f"❌ AI DEBUG: OpenAI error: {e}")
        print(f"❌ AI DEBUG: Falling back to enhanced responses")
        return get_enhanced_fallback_response(user_message, conversation_history, topic)

def get_enhanced_fallback_response(user_message, conversation_history, topic):
    """Enhanced fallback with conversation context awareness"""
    user_lower = user_message.lower()
    conversation_depth = len(conversation_history)
    
    # Analyze previous conversation for context and avoid repetition
    previous_topics = []
    recent_responses = []
    procrastination_mentions = 0
    
    for entry in conversation_history[-5:]:  # Last 5 messages
        content = entry['content'].lower()
        if entry['role'] == 'coach':
            recent_responses.append(content)
        
        # Track topics mentioned
        if 'fear' in content or 'scared' in content or 'afraid' in content:
            previous_topics.append('fear')
        if 'stress' in content or 'anxiety' in content or 'anxious' in content:
            previous_topics.append('stress')
        if 'confidence' in content:
            previous_topics.append('confidence')
        if 'procrastination' in content or 'procrastinate' in content:
            procrastination_mentions += 1
    
    # Avoid repetitive responses by checking recent coach messages
    def response_recently_used(phrase):
        return any(phrase in response for response in recent_responses[-2:])
    
    # Enhanced keyword detection with progression-based responses
    
    # Procrastination responses - vary based on conversation depth and mentions
    if any(word in user_lower for word in ['procrastination', 'procrastinate', 'putting off', 'delay', 'avoiding', 'struggle']):
        if procrastination_mentions == 0:  # First mention
            return {
                'message': "I hear that procrastination is showing up as a significant challenge for you. That takes courage to name directly. What do you notice about when procrastination tends to happen most for you?",
                'questions': [
                    "What tasks do you find yourself putting off most often?",
                    "What might be underneath the procrastination - fear, perfectionism, or something else?"
                ]
            }
        elif procrastination_mentions == 1:  # Second mention - dig deeper
            return {
                'message': "You've mentioned procrastination again, which tells me it's really central to what you're experiencing. Let's explore the pattern more deeply. What happens right before you start to procrastinate?",
                'questions': [
                    "What thoughts or feelings show up just before you avoid a task?",
                    "If procrastination wasn't an option, what would you do instead?"
                ]
            }
        else:  # Multiple mentions - focus on solutions and action
            return {
                'message': "I'm noticing procrastination keeps coming up in our conversation. This suggests we're touching on something really important. What would be one small step you could take today to break this pattern?",
                'questions': [
                    "What's the smallest possible action you could take on a challenging task right now?",
                    "What would success look like if you completed just one difficult task this week?"
                ]
            }
    
    # Fear and failure responses - progressive depth
    elif any(word in user_lower for word in ['fear', 'scared', 'afraid', 'failure', 'fail', 'worried']):
        if 'fear' not in previous_topics:
            return {
                'message': "I can hear that fear is playing a significant role in your experience. Fear of failure is incredibly common, and it takes real courage to name it. What do you think this fear is trying to protect you from?",
                'questions': [
                    "When you imagine completing the task successfully, what comes up for you?",
                    "What would it mean about you if you did fail at this task?"
                ]
            }
        else:
            return {
                'message': "Fear seems to be a central theme in what you're experiencing. I'm curious - when did you first learn to be afraid of failing? What message did you receive about making mistakes?",
                'questions': [
                    "What would you tell a good friend who was experiencing this same fear?",
                    "What evidence do you have that contradicts this fear?"
                ]
            }
    
    # Physical symptoms and body responses - validate and explore
    elif any(word in user_lower for word in ['body', 'shiver', 'sweat', 'profusely', 'physical', 'symptoms', 'jittery', 'gittery', 'run away']):
        return {
            'message': "I can hear how intensely your body is responding to these challenging situations. Your body is giving you important information about your stress response. It sounds like your nervous system is trying to protect you. What helps you feel most grounded when you notice these physical reactions?",
            'questions': [
                "What would it be like to approach a challenging task when your body feels calm and ready?",
                "What strategies have helped you manage anxiety in other areas of your life?"
            ]
        }
    
    # Goals and aspirations - shift toward action
    elif any(word in user_lower for word in ['want to', 'complete tasks', 'on time', 'without procrastination', 'reputation', 'opportunities']):
        if conversation_depth >= 4:  # Later in conversation - focus on concrete steps
            return {
                'message': "I hear how important this is to you - completing tasks on time and protecting your reputation. Given everything we've discussed about fear and procrastination, what would be one specific strategy you could try this week?",
                'questions': [
                    "What would completing tasks on time give you that you don't have now?",
                    "What's one task you've been putting off that you could commit to finishing this week?"
                ]
            }
        else:
            return {
                'message': "That's a powerful goal - completing tasks on time without procrastination. I can hear how much this matters to you, especially when you mention reputation and missed opportunities. What would change in your life if you achieved this?",
                'questions': [
                    "What would be different about how you feel about yourself?",
                    "What opportunities might open up for you?"
                ]
            }
    
    # Default responses - vary based on conversation depth
    if conversation_depth <= 2:
        return {
            'message': "Thank you for sharing that with me. I can sense there's a lot beneath the surface of what you're describing. What feels most important for us to explore together right now?",
            'questions': [
                "What would you most like to understand about this situation?",
                "If you could change one thing about how you handle challenging tasks, what would it be?"
            ]
        }
    else:
        theme_text = f" building on what we've discussed about {', '.join(set(previous_topics)[:2])}" if previous_topics else ""
        return {
            'message': f"I can hear the depth of what you're sharing{theme_text}. What insight or awareness is emerging for you as we talk about this?",
            'questions': [
                "What patterns are becoming clearer to you?",
                "What would you like to take away from our conversation today?"
            ]
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint for debugging"""
    return jsonify({
        'status': 'healthy',
        'app': 'AI Coaching Assistant - Adaptive Version',
        'openai_configured': bool(openai.api_key),
        'active_sessions': len(sessions),
        'timestamp': datetime.now().isoformat()
    })

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
        
        # Validate request data
        if not request.json:
            print(f"❌ AI SEND_MESSAGE: No JSON data in request")
            return jsonify({'error': 'No JSON data provided'}), 400
        
        data = request.json
        session_id = data.get('session_id')
        user_message = data.get('message')
        message_type = data.get('type', 'text')
        
        print(f"🔍 AI SEND_MESSAGE: session_id={session_id}, message='{user_message}', type={message_type}")
        
        if not session_id or not user_message:
            print(f"❌ AI SEND_MESSAGE: Missing required fields")
            return jsonify({'error': 'Missing session_id or message'}), 400
        
        # Check if session exists
        if session_id not in sessions:
            print(f"❌ AI SEND_MESSAGE: Session {session_id} not found")
            print(f"🔍 Available sessions: {list(sessions.keys())}")
            return jsonify({'error': 'Session not found'}), 404
        
        session = sessions[session_id]
        print(f"🔍 AI SEND_MESSAGE: Session found, current topic: {session.get('topic')}")
        
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
            
            try:
                response = get_ai_coaching_response(user_message, conversation_history, topic)
                print(f"🔍 AI SEND_MESSAGE: AI response generated: {response.get('ai_powered', False)}")
            except Exception as ai_error:
                print(f"❌ AI SEND_MESSAGE: AI response generation failed: {ai_error}")
                # Fallback to simple response
                response = {
                    'message': "Thank you for sharing that. I'm here to support you in exploring this further. What feels most important to focus on right now?",
                    'questions': ["What would you like to explore next?", "How can I best support you with this?"]
                }
        
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
        print(f"❌ AI SEND_MESSAGE: Unexpected error: {e}")
        print(f"❌ AI SEND_MESSAGE: Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        # Return a safe fallback response
        return jsonify({
            'error': 'Internal server error',
            'message': "I apologize, but I'm experiencing a technical issue. Could you please try again?",
            'questions': ["What would you like to explore?"],
            'stage': 'exploration'
        }), 500

if __name__ == '__main__':
    print("🚀 Starting AI-powered adaptive coaching app...")
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True) 
