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
openai_api_key = os.getenv('OPENAI_API_KEY')

# Don't set global api_key to avoid conflicts with new client syntax
# openai.api_key = os.getenv('OPENAI_API_KEY')

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

def save_session_to_db(session_id, session_data):
    """Save session to database"""
    try:
        conn = sqlite3.connect('coaching_sessions.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO sessions 
            (id, user_id, topic, current_stage, conversation_history, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id,
            session_data.get('user_id'),
            session_data.get('topic'),
            session_data.get('stage'),
            json.dumps(session_data.get('conversation_history', [])),
            session_data.get('created_at'),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        print(f"✅ Session {session_id} saved to database")
    except Exception as e:
        print(f"❌ Failed to save session to database: {e}")

def load_session_from_db(session_id):
    """Load session from database"""
    try:
        conn = sqlite3.connect('coaching_sessions.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            session_data = {
                'session_id': row[0],
                'user_id': row[1],
                'topic': row[2],
                'stage': row[3],
                'conversation_history': json.loads(row[4]) if row[4] else [],
                'created_at': row[6]
            }
            print(f"✅ Session {session_id} loaded from database")
            return session_data
        else:
            print(f"❌ Session {session_id} not found in database")
            return None
    except Exception as e:
        print(f"❌ Failed to load session from database: {e}")
        return None

def get_ai_coaching_response(user_message, conversation_history, topic):
    """Generate AI-powered adaptive coaching response"""
    try:
        # Check if OpenAI API key is available
        if not openai_api_key:
            print("⚠️ No OpenAI API key found, using enhanced fallback")
            return get_enhanced_fallback_response(user_message, conversation_history, topic)
        
        print(f"🔑 OpenAI API key configured: {openai_api_key[:10]}...{openai_api_key[-4:]}")
        
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
        
        # Use direct requests approach for better reliability
        try:
            import requests
            import json
            
            headers = {
                'Authorization': f'Bearer {openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': messages,
                'max_tokens': 200,
                'temperature': 0.7
            }
            
            print("🌐 Making direct HTTP request to OpenAI API")
            http_response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=15
            )
            
            if http_response.status_code == 200:
                result = http_response.json()
                ai_message = result['choices'][0]['message']['content'].strip()
                print("✅ AI DEBUG: Direct HTTP request successful")
            else:
                print(f"❌ HTTP request failed: {http_response.status_code} - {http_response.text}")
                return get_enhanced_fallback_response(user_message, conversation_history, topic)
                
        except Exception as api_error:
            print(f"❌ AI DEBUG: OpenAI API request failed: {api_error}")
            error_str = str(api_error).lower()
            if "quota" in error_str or "billing" in error_str:
                print("💡 Issue: Insufficient quota or billing problem")
            elif "authentication" in error_str or "api_key" in error_str:
                print("💡 Issue: API key authentication failed")
            else:
                print(f"💡 Issue: {api_error}")
            return get_enhanced_fallback_response(user_message, conversation_history, topic)
        
        # Extract questions from the response (improved extraction)
        import re
        
        # Find all sentences that end with question marks
        question_pattern = r'([^.!?]*\?)'
        found_questions = re.findall(question_pattern, ai_message)
        
        # Clean up and filter questions
        questions = []
        for q in found_questions:
            q = q.strip().strip('- ').strip()
            # Filter out very short or generic questions
            if len(q) > 15 and not q.lower().startswith('what do you think'):
                questions.append(q)
        
        # Take last 2 questions if multiple found
        questions = questions[-2:] if len(questions) > 2 else questions
        
        # If no good questions found, generate coaching questions based on content
        if not questions:
            if 'fear' in ai_message.lower() or 'afraid' in ai_message.lower():
                questions = [
                    "What would it look like to approach this with curiosity instead of fear?",
                    "What evidence do you have that contradicts this fear?"
                ]
            elif 'procrastination' in ai_message.lower() or 'delay' in ai_message.lower():
                questions = [
                    "What would help you take the first step on a challenging task?",
                    "What patterns do you notice about when procrastination shows up?"
                ]
            else:
                questions = [
                    "What patterns are you noticing as we explore this?",
                    "What feels most important for you to understand about this situation?"
                ]
        
        print(f"✅ AI DEBUG: OpenAI response generated successfully")
        print(f"🔍 AI DEBUG: Extracted {len(questions)} questions: {questions}")
        return {
            'message': ai_message,
            'questions': questions,
            'ai_powered': True
        }
        
    except Exception as e:
        print(f"❌ AI DEBUG: Unexpected error in OpenAI function: {e}")
        print(f"❌ AI DEBUG: Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return get_enhanced_fallback_response(user_message, conversation_history, topic)

def get_enhanced_fallback_response(user_message, conversation_history, topic):
    """Enhanced fallback with conversation context awareness"""
    user_lower = user_message.lower()
    conversation_depth = len(conversation_history)
    
    # Analyze previous conversation for context and avoid repetition
    previous_topics = []
    recent_responses = []
    procrastination_mentions = 0
    fear_mentions = 0
    insight_indicators = []
    
    for entry in conversation_history[-8:]:  # Last 8 messages for better context
        content = entry['content'].lower()
        if entry['role'] == 'coach':
            recent_responses.append(content)
        
        # Track topics mentioned
        if 'fear' in content or 'scared' in content or 'afraid' in content or 'worried' in content:
            previous_topics.append('fear')
            fear_mentions += 1
        if 'stress' in content or 'anxiety' in content or 'anxious' in content:
            previous_topics.append('stress')
        if 'confidence' in content:
            previous_topics.append('confidence')
        if 'procrastination' in content or 'procrastinate' in content:
            procrastination_mentions += 1
    
    # Detect insight-sharing vs problem-stating
    sharing_insights = any(phrase in user_lower for phrase in [
        'when i started', 'i learned', 'i realized', 'i think', 'i believe', 
        'eventually i', 'i was able to', 'has stayed with me', 'i got better',
        'i discovered', 'i found that', 'looking back', 'now i see'
    ])
    
    # Detect progress or capability mentions
    showing_growth = any(phrase in user_lower for phrase in [
        'got better', 'improved', 'eventually', 'was able to', 'learned',
        'overcame', 'managed to', 'succeeded', 'figured out'
    ])
    
    # Avoid repetitive responses by checking recent coach messages
    def response_recently_used(phrase):
        return any(phrase.lower() in response for response in recent_responses[-2:])
    
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
    
    # Fear and failure responses - progressive depth with better progression
    elif any(word in user_lower for word in ['fear', 'scared', 'afraid', 'failure', 'fail', 'worried']):
        if fear_mentions == 0:  # First fear mention
            return {
                'message': "I can hear that fear is playing a significant role in your experience. Fear of failure is incredibly common, and it takes real courage to name it. What do you think this fear is trying to protect you from?",
                'questions': [
                    "When you imagine completing the task successfully, what comes up for you?",
                    "What would it mean about you if you did fail at this task?"
                ]
            }
        elif fear_mentions == 1 and not sharing_insights:  # Second mention, still exploring
            return {
                'message': "Fear seems to be a central theme in what you're experiencing. I'm curious - when did you first learn to be afraid of failing? What message did you receive about making mistakes?",
                'questions': [
                    "What would you tell a good friend who was experiencing this same fear?",
                    "What evidence do you have that contradicts this fear?"
                ]
            }
        elif sharing_insights and showing_growth:  # They're sharing personal history and growth
            return {
                'message': "Thank you for sharing that personal experience with coding and overcoming those initial roadblocks. It sounds like you've actually proven to yourself that you can work through challenges and get better. What do you think helped you push through those coding fears back then?",
                'questions': [
                    "How might you apply what you learned from getting better at coding to your current challenges?",
                    "What would it look like to trust your ability to 'eventually get better' at new complex tasks?"
                ]
            }
        elif sharing_insights:  # Sharing insights but not necessarily showing growth
            return {
                'message': "I appreciate you sharing the origin of this fear - that moment when coding roadblocks first triggered that fear of failing. It takes real self-awareness to connect current patterns to past experiences. What do you notice about how this early fear might be influencing you now?",
                'questions': [
                    "How has this fear served you over the years, and how might it be limiting you now?",
                    "What would you need to feel more confident when facing new complex challenges?"
                ]
            }
        else:  # Multiple fear mentions - focus on moving forward with variation
            # Avoid repetition by checking if we just asked about taking action
            if 'take the first step' in user_lower or 'overcome this fear' in user_lower:
                return {
                    'message': "I can hear your readiness to move beyond this fear pattern. That's a powerful shift from feeling stuck to wanting action. What would taking just one small step look like for you?",
                    'questions': [
                        "What's the smallest possible first step you could take on a complex task?",
                        "What support or resources would make that first step feel more manageable?"
                    ]
                }
            else:
                return {
                    'message': "I'm hearing how deeply this fear has influenced your relationship with challenging tasks. Given everything you've shared about where this fear comes from, what feels most important to address right now?",
                    'questions': [
                        "What would be different if you could approach complex tasks with curiosity instead of fear?",
                        "What's one way you could start building evidence that you can handle challenging work?"
                    ]
                }
    
    # Complex tasks and time pressure responses
    elif any(word in user_lower for word in ['complex activity', 'assigned', 'complete it on time', 'roadblocks', 'hit roadblocks']):
        if showing_growth:
            return {
                'message': "I'm struck by something important in what you shared - you mentioned hitting roadblocks when coding but eventually getting better at it. That tells me you have experience working through complexity and succeeding. What helped you persist through those coding challenges?",
                'questions': [
                    "What strategies did you use when you got stuck on coding problems?",
                    "How can you apply that same persistence to other complex activities you face now?"
                ]
            }
        else:
            return {
                'message': "It sounds like complex activities trigger a cascade of worry - about time, capability, and whether to engage at all. That's a lot of mental energy going into just deciding whether to start. What would it feel like to approach a complex task with confidence?",
                'questions': [
                    "What would need to be different for you to feel ready to tackle complexity?",
                    "When you do successfully complete complex work, what conditions helped you succeed?"
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
    
    # Default responses - vary based on conversation depth and insights shared
    if sharing_insights and conversation_depth >= 3:
        return {
            'message': "I can hear the self-reflection and awareness in what you're sharing. You're making connections between past experiences and current patterns. What insights are becoming clearer for you through our conversation?",
            'questions': [
                "What feels most important to take away from what we've explored?",
                "How might you use these insights to approach challenges differently?"
            ]
        }
    elif conversation_depth <= 2:
        return {
            'message': "Thank you for sharing that with me. I can sense there's a lot beneath the surface of what you're describing. What feels most important for us to explore together right now?",
            'questions': [
                "What would you most like to understand about this situation?",
                "If you could change one thing about how you handle challenging tasks, what would it be?"
            ]
        }
    else:
        # Fix the set slicing bug by converting to list first
        unique_topics = list(set(previous_topics))[:2]
        theme_text = f" building on what we've discussed about {', '.join(unique_topics)}" if unique_topics else ""
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
        'openai_configured': bool(openai_api_key),
        'active_sessions': len(sessions),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/start-session', methods=['POST'])
def start_session():
    """Start a new coaching session - AI POWERED VERSION"""
    try:
        print(f"🔍 AI START_SESSION: Starting new session...")
        print(f"🔍 AI START_SESSION: Request method: {request.method}")
        print(f"🔍 AI START_SESSION: Request content type: {request.content_type}")
        
        # Check if request has JSON data
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json()
            print(f"🔍 AI START_SESSION: Request data: {data}")
        else:
            print(f"🔍 AI START_SESSION: No JSON data in request")
        
        print(f"🔍 AI START_SESSION: Generating IDs...")
        user_id = str(uuid.uuid4())
        session_id = str(uuid.uuid4())
        
        print(f"🔍 AI START_SESSION: user_id={user_id}, session_id={session_id}")
        
        print(f"🔍 AI START_SESSION: Creating session object...")
        # Store in memory with conversation history
        session_data = {
            'user_id': user_id,
            'session_id': session_id,
            'stage': 'intake',
            'topic': None,
            'conversation_history': [],
            'created_at': datetime.now().isoformat()
        }
        
        print(f"🔍 AI START_SESSION: Storing session in memory and database...")
        sessions[session_id] = session_data
        save_session_to_db(session_id, session_data)
        print(f"🔍 AI START_SESSION: Session stored. Total sessions: {len(sessions)}")
        
        print(f"🔍 AI START_SESSION: Creating response object...")
        # Simple response
        response_data = {
            'message': 'Welcome to your coaching session! I\'m here to support you in exploring what\'s important to you. This is a confidential space where you can share openly.',
            'questions': [
                'What brings you to coaching right now?',
                'What would you like to explore in this session?', 
                'How can I best support you today?'
            ],
            'stage': 'intake',
            'available_topics': ['performance_improvement', 'career_development', 'work_life_balance', 'leadership_growth']
        }
        
        print(f"🔍 AI START_SESSION: Creating final JSON response...")
        final_response = {
            'session_id': session_id,
            'user_id': user_id,
            'response': response_data
        }
        
        print(f"✅ AI START_SESSION: Session created successfully")
        return jsonify(final_response)
        
    except Exception as e:
        print(f"❌ AI START_SESSION: Error occurred: {e}")
        print(f"❌ AI START_SESSION: Error type: {type(e).__name__}")
        import traceback
        print(f"❌ AI START_SESSION: Full traceback:")
        traceback.print_exc()
        
        error_response = {'error': f'Failed to start session: {str(e)}'}
        print(f"❌ AI START_SESSION: Returning error response: {error_response}")
        return jsonify(error_response), 500

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
        
        # Check if session exists in memory first, then database
        session = None
        if session_id in sessions:
            session = sessions[session_id]
            print(f"🔍 AI SEND_MESSAGE: Session found in memory")
        else:
            print(f"🔍 AI SEND_MESSAGE: Session not in memory, checking database...")
            session = load_session_from_db(session_id)
            if session:
                sessions[session_id] = session  # Cache in memory
                print(f"🔍 AI SEND_MESSAGE: Session loaded from database and cached")
        
        if not session:
            print(f"❌ AI SEND_MESSAGE: Session {session_id} not found in memory or database")
            print(f"🔍 Available sessions: {list(sessions.keys())}")
            return jsonify({'error': 'Session not found'}), 404
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
        
        # Save updated session to database
        save_session_to_db(session_id, session)
        
        # Update response with standard fields
        response.update({
            'stage': 'exploration',
            'competency_applied': 'active_listening',
            'ai_confidence': 0.9,
            'demo_mode': not response.get('ai_powered', False),  # True only if NOT AI-powered
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
