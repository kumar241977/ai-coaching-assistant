from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
import json
from datetime import datetime
import threading
import time
from icf_competencies import ICFCompetencyFramework, ICFCompetency
from openai_coaching import OpenAICoachingEngine, CoachingContext

class ConversationStage(Enum):
    INTAKE = "intake"
    EXPLORATION = "exploration"
    REFLECTION = "reflection"
    ACTION_PLANNING = "action_planning"
    FOLLOW_UP = "follow_up"

@dataclass
class CoachingTopic:
    name: str
    description: str
    initial_questions: List[str]
    exploration_areas: List[str]

@dataclass
class ConversationState:
    user_id: str
    session_id: str
    current_stage: ConversationStage
    topic: Optional[CoachingTopic]
    conversation_history: List[Dict[str, Any]]
    insights: List[str]
    actions: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

class ConversationFlowEngine:
    def __init__(self):
        self.icf_framework = ICFCompetencyFramework()
        self.coaching_topics = self._initialize_coaching_topics()
        self.sessions = {}  # In-memory storage, replace with database in production
        self.openai_coach = None  # Lazy initialization - will be created when first needed
    
    def _get_openai_coach(self):
        """Get OpenAI coach with timeout handling and detailed logging"""
        if self.openai_coach is None:
            print("🔍 DEBUG: Starting OpenAI coach initialization...")
            
            # Use timeout to prevent indefinite hanging
            initialization_result = [None, None]  # [coach_instance, error]
            
            def init_openai_coach():
                try:
                    print("🔍 DEBUG: About to import OpenAICoachingEngine...")
                    from openai_coaching import OpenAICoachingEngine
                    print("🔍 DEBUG: OpenAICoachingEngine imported successfully")
                    
                    print("🔍 DEBUG: About to create OpenAICoachingEngine instance...")
                    coach = OpenAICoachingEngine()
                    print("🔍 DEBUG: OpenAICoachingEngine instance created successfully")
                    
                    initialization_result[0] = coach
                    print("✅ OpenAI Coach: Initialized successfully with timeout protection")
                except Exception as e:
                    print(f"❌ DEBUG: OpenAI initialization error: {e}")
                    print(f"❌ DEBUG: Error type: {type(e).__name__}")
                    import traceback
                    traceback.print_exc()
                    initialization_result[1] = e
            
            # Start initialization in a separate thread
            print("🔍 DEBUG: Starting initialization thread...")
            init_thread = threading.Thread(target=init_openai_coach, daemon=True)
            init_thread.start()
            
            # Wait with timeout (30 seconds max)
            print("🔍 DEBUG: Waiting for initialization (30s timeout)...")
            init_thread.join(timeout=30.0)
            
            if init_thread.is_alive():
                print("⚠️ DEBUG: OpenAI initialization timed out after 30 seconds - using fallback")
                self.openai_coach = self._create_enhanced_fallback_coach()
            elif initialization_result[0] is not None:
                print("✅ DEBUG: OpenAI initialization completed successfully")
                self.openai_coach = initialization_result[0]
            else:
                error = initialization_result[1] or "Unknown error"
                print(f"❌ DEBUG: OpenAI initialization failed: {error}")
                self.openai_coach = self._create_enhanced_fallback_coach()
        
        return self.openai_coach
    
    def _create_enhanced_fallback_coach(self):
        """Create an enhanced fallback coach with better intelligence"""
        class EnhancedFallbackCoach:
            def __init__(self):
                self.conversation_history = []
                self.topic_context = None
                
            def generate_coaching_response(self, context, user_input):
                # Store context for better responses
                if context:
                    self.topic_context = context.topic
                
                # Add to conversation history for context
                if user_input:
                    self.conversation_history.append(user_input.lower())
                
                # Enhanced topic-based responses with conversation depth awareness
                conversation_depth = len(self.conversation_history)
                
                # Determine response based on conversation depth and content
                if conversation_depth <= 1:
                    # Initial/topic selection responses
                    return self._get_initial_response(user_input)
                elif conversation_depth <= 3:
                    # Early exploration responses
                    return self._get_exploration_response(user_input)
                else:
                    # Deeper conversation responses
                    return self._get_deeper_response(user_input)
            
            def _get_initial_response(self, user_input):
                user_lower = user_input.lower() if user_input else ""
                
                if any(word in user_lower for word in ['performance', 'productivity', 'work better', 'effectiveness']):
                    return {
                        "message": "I understand you're working on performance improvement. That's a valuable area to focus on. What specific aspects of your performance feel most important to address right now?",
                        "questions": [
                            "What does peak performance look like for you?",
                            "What obstacles are currently impacting your effectiveness?",
                            "What strengths can you build upon to improve your performance?"
                        ],
                        "competency_applied": "establishing_trust_and_intimacy",
                        "confidence": 0.8,
                        "demo_mode": True
                    }
                # Add similar blocks for other topics...
                else:
                    return {
                        "message": "Thank you for sharing that with me. I can sense this is important to you. Can you help me understand more about what you're experiencing?",
                        "questions": [
                            "What would you like to explore further about this?",
                            "How is this situation affecting you?",
                            "What aspects feel most significant to you?"
                        ],
                        "competency_applied": "active_listening",
                        "confidence": 0.7,
                        "demo_mode": True
                    }
            
            def _get_exploration_response(self, user_input):
                # Analyze user input for emotional content and themes
                user_lower = user_input.lower() if user_input else ""
                
                if any(word in user_lower for word in ['procrastination', 'procrastinate', 'putting off', 'delay', 'avoiding']):
                    return {
                        "message": "I hear that procrastination is showing up as a significant challenge for you. That's something many people struggle with, and it takes courage to name it directly. What do you notice about when procrastination tends to happen most for you?",
                        "questions": [
                            "What tasks or situations do you find yourself putting off most often?",
                            "What do you think might be underneath the procrastination - fear, perfectionism, or something else?",
                            "When you do manage to take action despite the urge to procrastinate, what helps you push through?"
                        ],
                        "competency_applied": "active_listening",
                        "confidence": 0.9,
                        "demo_mode": True
                    }
                elif any(word in user_lower for word in ['stressed', 'overwhelmed', 'pressure']):
                    return {
                        "message": "I can hear that you're feeling stressed and overwhelmed. That sounds really challenging. What do you think is contributing most to that feeling of pressure?",
                        "questions": [
                            "When do you notice the stress is most intense?",
                            "What would it feel like to have less pressure in this area?",
                            "What support would be most helpful right now?"
                        ],
                        "competency_applied": "active_listening",
                        "confidence": 0.8,
                        "demo_mode": True
                    }
                elif any(word in user_lower for word in ['confused', 'unclear', 'not sure']):
                    return {
                        "message": "It sounds like there's some uncertainty here, which is completely understandable. What aspect would you like to get clearer on first?",
                        "questions": [
                            "What would clarity in this situation look like for you?",
                            "What information or perspective might help you feel more certain?",
                            "What feels most important to understand right now?"
                        ],
                        "competency_applied": "powerful_questioning",
                        "confidence": 0.8,
                        "demo_mode": True
                    }
                elif any(word in user_lower for word in ['focus', 'distracted', 'concentration']):
                    return {
                        "message": "Focus and concentration challenges can really impact how we feel about our performance. It sounds like this is affecting you in meaningful ways. What have you noticed about your focus patterns?",
                        "questions": [
                            "When do you find your focus is strongest?",
                            "What distractions tend to pull you away most often?",
                            "What does your ideal focus environment look like?"
                        ],
                        "competency_applied": "creating_awareness",
                        "confidence": 0.8,
                        "demo_mode": True
                    }
                else:
                    return {
                        "message": f"Thank you for sharing that with me. I can sense this is important to you - '{user_input}'. What stands out most to you as we explore this together?",
                        "questions": [
                            "What patterns are you noticing as we talk about this?",
                            "What insights are emerging for you?",
                            "How has this been affecting other areas of your life or work?"
                        ],
                        "competency_applied": "creating_awareness",
                        "confidence": 0.7,
                        "demo_mode": True
                    }
            
            def _get_deeper_response(self, user_input):
                # More sophisticated responses for deeper conversation
                return {
                    "message": "You've shared some really valuable insights. I'm curious about what you're discovering about yourself through this exploration. What feels like the most important realization?",
                    "questions": [
                        "What actions are you feeling drawn to take?",
                        "What would be different if you made this change?",
                        "What first step feels most meaningful to you?"
                    ],
                    "competency_applied": "designing_actions",
                    "confidence": 0.8,
                    "demo_mode": True
                }
            
            def reset_conversation_state(self):
                self.conversation_history = []
                self.topic_context = None
                
        return EnhancedFallbackCoach()
    
    def _initialize_coaching_topics(self) -> Dict[str, CoachingTopic]:
        return {
            "performance_improvement": CoachingTopic(
                name="Performance Improvement",
                description="Enhancing work performance and productivity",
                initial_questions=[
                    "What specific aspect of your performance would you like to improve?",
                    "What's currently working well in your performance?",
                    "What challenges are you facing that impact your performance?"
                ],
                exploration_areas=["skills", "motivation", "resources", "feedback", "goals"]
            ),
            
            "career_development": CoachingTopic(
                name="Career Development",
                description="Planning and advancing career growth",
                initial_questions=[
                    "Where do you see yourself in your career journey?",
                    "What career aspirations are most important to you?",
                    "What's holding you back from your next career step?"
                ],
                exploration_areas=["aspirations", "skills_gap", "networking", "opportunities", "barriers"]
            ),
            
            "work_life_balance": CoachingTopic(
                name="Work-Life Balance",
                description="Achieving harmony between professional and personal life",
                initial_questions=[
                    "How would you describe your current work-life balance?",
                    "What areas of your life feel out of balance?",
                    "What would ideal balance look like for you?"
                ],
                exploration_areas=["boundaries", "priorities", "time_management", "energy", "values"]
            ),
            
            "leadership_growth": CoachingTopic(
                name="Leadership Growth",
                description="Developing leadership skills and effectiveness",
                initial_questions=[
                    "What kind of leader do you want to be?",
                    "What leadership challenges are you currently facing?",
                    "How do you currently influence and inspire others?"
                ],
                exploration_areas=["leadership_style", "influence", "team_dynamics", "decision_making", "vision"]
            )
        }
    
    def start_new_session(self, user_id: str, session_id: str = None) -> ConversationState:
        """Start a new coaching session"""
        if session_id is None:
            session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Reset conversation state for fresh start
        self._get_openai_coach().reset_conversation_state()
        
        state = ConversationState(
            user_id=user_id,
            session_id=session_id,
            current_stage=ConversationStage.INTAKE,
            topic=None,
            conversation_history=[],
            insights=[],
            actions=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.sessions[session_id] = state
        return state
    
    def get_session(self, session_id: str) -> Optional[ConversationState]:
        """Retrieve existing session"""
        return self.sessions.get(session_id)
    
    def generate_intake_response(self, state: ConversationState) -> Dict[str, Any]:
        """Generate response for intake stage"""
        competency = self.icf_framework.get_competency_response(ICFCompetency.ESTABLISHING_TRUST)
        
        return {
            "message": "Welcome to your coaching session. I'm here to support you in exploring what's important to you. This is a confidential space where you can share openly.",
            "questions": [
                "What would you like to work on in today's session?",
                "What brings you to coaching right now?",
                "How can I best support you today?"
            ],
            "stage": "intake",
            "competency_applied": competency.competency.value,
            "available_topics": list(self.coaching_topics.keys())
        }
    
    def process_topic_selection(self, state: ConversationState, topic_key: str) -> Dict[str, Any]:
        """Process user's topic selection and move to exploration"""
        if topic_key not in self.coaching_topics:
            return {"error": "Invalid topic selected"}
        
        state.topic = self.coaching_topics[topic_key]
        state.current_stage = ConversationStage.EXPLORATION
        state.updated_at = datetime.now()
        
        competency = self.icf_framework.get_competency_response(ICFCompetency.ESTABLISHING_TRUST)
        
        # Create a more appropriate initial message for topic selection
        topic_messages = {
            "performance_improvement": f"Excellent choice! Let's explore {state.topic.name} together. I'm here to support you in discovering what's working well and what you'd like to enhance. This is a safe space to share your experiences openly.",
            "career_development": f"Great! {state.topic.name} is such an important area. I'm excited to explore your career aspirations and help you identify the next steps in your professional journey.",
            "work_life_balance": f"Thank you for choosing to work on {state.topic.name}. Finding harmony between different aspects of life is crucial for well-being. Let's explore what balance means to you.",
            "leadership_growth": f"Wonderful! {state.topic.name} is a powerful area for development. I'm here to support you in discovering your authentic leadership style and expanding your influence."
        }
        
        initial_message = topic_messages.get(topic_key, f"Great! Let's explore {state.topic.name} together. I'm here to support you through this coaching conversation.")
        
        return {
            "message": initial_message,
            "questions": state.topic.initial_questions,
            "stage": "exploration", 
            "competency_applied": competency.competency.value,
            "topic": state.topic.name
        }
    
    def generate_exploration_response(self, state: ConversationState, user_input: str) -> Dict[str, Any]:
        """Generate response for exploration stage using OpenAI intelligent coaching"""
        # Add user input to conversation history
        self._add_to_history(state, "user", user_input)
        
        # Determine which competency to apply based on conversation depth
        conversation_depth = len([msg for msg in state.conversation_history if msg["role"] == "user"])
        
        if conversation_depth <= 2:
            icf_competency = "active_listening"
        else:
            icf_competency = "powerful_questioning"
        
        # Create coaching context for OpenAI
        coaching_context = CoachingContext(
            topic=state.topic.name if state.topic else "General Coaching",
            stage="exploration",
            conversation_history=state.conversation_history,
            user_emotional_state="engaged",  # Could be enhanced with NLP analysis
            icf_competency=icf_competency,
            session_goals=[]  # Could be populated based on user's stated goals
        )
        
        # Generate intelligent response using OpenAI
        ai_response = self._get_openai_coach().generate_coaching_response(coaching_context, user_input)
        
        return {
            "message": ai_response["message"],
            "questions": ai_response["questions"][:2],  # Limit to 2 best questions
            "stage": "exploration",
            "competency_applied": ai_response["competency_applied"],
            "suggested_next_stage": ai_response.get("suggested_next_stage", "exploration"),
            "ai_confidence": ai_response.get("confidence", 0.8),
            "demo_mode": ai_response.get("demo_mode", False)
        }
    
    def generate_reflection_response(self, state: ConversationState, user_input: str) -> Dict[str, Any]:
        """Generate response for reflection stage using OpenAI creating awareness competency"""
        self._add_to_history(state, "user", user_input)
        
        # Create coaching context for reflection stage
        coaching_context = CoachingContext(
            topic=state.topic.name if state.topic else "General Coaching",
            stage="reflection",
            conversation_history=state.conversation_history,
            user_emotional_state="reflective",
            icf_competency="creating_awareness",
            session_goals=[]
        )
        
        # Generate intelligent response using OpenAI
        ai_response = self._get_openai_coach().generate_coaching_response(coaching_context, user_input)
        
        # Generate insights based on conversation history
        insights = self._generate_insights(state)
        state.insights.extend(insights)
        
        return {
            "message": ai_response["message"],
            "questions": ai_response["questions"],
            "stage": "reflection",
            "competency_applied": ai_response["competency_applied"],
            "insights": insights,
            "suggested_next_stage": ai_response.get("suggested_next_stage", "action_planning"),
            "ai_confidence": ai_response.get("confidence", 0.8),
            "demo_mode": ai_response.get("demo_mode", False)
        }
    
    def generate_action_planning_response(self, state: ConversationState, user_input: str) -> Dict[str, Any]:
        """Generate response for action planning stage using OpenAI"""
        self._add_to_history(state, "user", user_input)
        
        # Create coaching context for action planning stage
        coaching_context = CoachingContext(
            topic=state.topic.name if state.topic else "General Coaching",
            stage="action_planning",
            conversation_history=state.conversation_history,
            user_emotional_state="ready_for_action",
            icf_competency="designing_actions",
            session_goals=[]
        )
        
        # Generate intelligent response using OpenAI
        ai_response = self._get_openai_coach().generate_coaching_response(coaching_context, user_input)
        
        return {
            "message": ai_response["message"],
            "questions": ai_response["questions"],
            "stage": "action_planning",
            "competency_applied": ai_response["competency_applied"],
            "suggested_next_stage": ai_response.get("suggested_next_stage", "action_planning"),
            "ai_confidence": ai_response.get("confidence", 0.8),
            "demo_mode": ai_response.get("demo_mode", False),
            "action_template": {
                "action": "",
                "by_when": "",
                "success_criteria": "",
                "potential_obstacles": "",
                "support_needed": ""
            }
        }
    
    def generate_follow_up_response(self, state: ConversationState, user_input: str) -> Dict[str, Any]:
        """Generate response for follow-up stage using OpenAI"""
        self._add_to_history(state, "user", user_input)
        
        # Create coaching context for follow-up stage
        coaching_context = CoachingContext(
            topic=state.topic.name if state.topic else "General Coaching",
            stage="follow_up",
            conversation_history=state.conversation_history,
            user_emotional_state="committed_to_action",
            icf_competency="managing_progress_and_accountability",
            session_goals=[]
        )
        
        # Generate intelligent response using OpenAI
        ai_response = self._get_openai_coach().generate_coaching_response(coaching_context, user_input)
        
        return {
            "message": ai_response["message"],
            "questions": ai_response["questions"],
            "stage": "follow_up",
            "competency_applied": ai_response["competency_applied"],
            "suggested_next_stage": ai_response.get("suggested_next_stage", "follow_up"),
            "ai_confidence": ai_response.get("confidence", 0.8),
            "demo_mode": ai_response.get("demo_mode", False),
            "session_summary": {
                "topic_explored": state.topic.name if state.topic else "General Coaching",
                "key_insights": state.insights[-3:] if state.insights else [],  # Last 3 insights
                "actions_committed": len(state.actions),
                "next_steps": "Continue implementing your action plan and reflect on progress"
            }
        }
    
    def process_action_commitment(self, state: ConversationState, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and store action commitment"""
        action_commitment = {
            "action": action_data.get("action", ""),
            "by_when": action_data.get("by_when", ""),
            "success_criteria": action_data.get("success_criteria", ""),
            "potential_obstacles": action_data.get("potential_obstacles", ""),
            "support_needed": action_data.get("support_needed", ""),
            "committed_at": datetime.now().isoformat()
        }
        
        state.actions.append(action_commitment)
        state.updated_at = datetime.now()
        
        return {
            "message": "Thank you for making that commitment. I'm confident you can achieve this.",
            "action_summary": action_commitment,
            "stage": "session_complete",
            "next_steps": "We can schedule a follow-up to review your progress."
        }
    
    def _add_to_history(self, state: ConversationState, role: str, content: str):
        """Add message to conversation history"""
        state.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def _generate_insights(self, state: ConversationState) -> List[str]:
        """Generate meaningful insights based on conversation content"""
        insights = []
        user_messages = [msg["content"] for msg in state.conversation_history if msg["role"] == "user"]
        
        if len(user_messages) < 2:
            return insights
        
        # Analyze conversation content for patterns
        conversation_text = " ".join(user_messages).lower()
        
        # Identify key themes and patterns
        if "procrastination" in conversation_text or "procrastinate" in conversation_text:
            if "fear" in conversation_text or "scared" in conversation_text:
                insights.append("Your procrastination appears to be connected to fear and self-doubt about your capabilities.")
            if "new" in conversation_text and "task" in conversation_text:
                insights.append("New or unfamiliar tasks seem to trigger your procrastination response.")
            if "confidence" in conversation_text:
                insights.append("Building self-confidence appears to be key to overcoming your procrastination patterns.")
        
        if "stress" in conversation_text or "overwhelm" in conversation_text:
            if "mind" in conversation_text and "background" in conversation_text:
                insights.append("Unfinished tasks create mental stress by running continuously in the background of your mind.")
        
        if "growth mindset" in conversation_text or "growth" in conversation_text:
            insights.append("You're ready to shift from a fixed to a growth mindset when facing challenges.")
        
        if "comfort zone" in conversation_text:
            insights.append("Moving beyond your comfort zone is where your greatest growth opportunities lie.")
        
        # Self-awareness insights
        if "realize" in conversation_text or "notice" in conversation_text:
            insights.append("Your self-awareness about these patterns is already a significant step toward change.")
        
        # Default insights if no specific patterns found
        if not insights and len(user_messages) >= 3:
            insights.append("You're showing great courage by exploring these challenging areas of your life.")
            insights.append("I notice you have strong self-reflection skills that will serve you well.")
        
        return insights[:2]  # Return max 2 most relevant insights 
