from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
import json
from datetime import datetime
from icf_competencies import ICFCompetencyFramework, ICFCompetency

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
        
        competency = self.icf_framework.get_competency_response(ICFCompetency.ACTIVE_LISTENING)
        
        return {
            "message": f"Great, let's explore {state.topic.name}. {competency.response_template}",
            "questions": state.topic.initial_questions,
            "stage": "exploration",
            "competency_applied": competency.competency.value,
            "topic": state.topic.name
        }
    
    def generate_exploration_response(self, state: ConversationState, user_input: str) -> Dict[str, Any]:
        """Generate response for exploration stage using active listening and powerful questioning"""
        # Add user input to conversation history
        self._add_to_history(state, "user", user_input)
        
        # Determine which competency to apply based on conversation depth
        conversation_depth = len([msg for msg in state.conversation_history if msg["role"] == "user"])
        
        if conversation_depth <= 2:
            competency = self.icf_framework.get_competency_response(ICFCompetency.ACTIVE_LISTENING)
            response_type = "clarification"
        else:
            competency = self.icf_framework.get_competency_response(ICFCompetency.POWERFUL_QUESTIONING)
            response_type = "deeper_exploration"
        
        return {
            "message": self._generate_contextual_response(user_input, competency, response_type),
            "questions": competency.follow_up_questions[:2],  # Limit to 2 questions
            "stage": "exploration",
            "competency_applied": competency.competency.value,
            "suggested_next_stage": "reflection" if conversation_depth >= 3 else "exploration"
        }
    
    def generate_reflection_response(self, state: ConversationState, user_input: str) -> Dict[str, Any]:
        """Generate response for reflection stage using creating awareness competency"""
        self._add_to_history(state, "user", user_input)
        
        competency = self.icf_framework.get_competency_response(ICFCompetency.CREATING_AWARENESS)
        
        # Generate insights based on conversation history
        insights = self._generate_insights(state)
        state.insights.extend(insights)
        
        return {
            "message": f"I'm noticing some patterns in what you've shared. {insights[0] if insights else 'What patterns do you see in what we\'ve discussed?'}",
            "questions": competency.follow_up_questions[:3],
            "stage": "reflection",
            "competency_applied": competency.competency.value,
            "insights": insights,
            "suggested_next_stage": "action_planning"
        }
    
    def generate_action_planning_response(self, state: ConversationState, user_input: str) -> Dict[str, Any]:
        """Generate response for action planning stage"""
        self._add_to_history(state, "user", user_input)
        
        competency = self.icf_framework.get_competency_response(ICFCompetency.DESIGNING_ACTIONS)
        
        return {
            "message": "Based on our conversation and the insights you've gained, what feels like the most important action you could take?",
            "questions": competency.follow_up_questions,
            "stage": "action_planning",
            "competency_applied": competency.competency.value,
            "action_template": {
                "action": "",
                "by_when": "",
                "success_criteria": "",
                "potential_obstacles": "",
                "support_needed": ""
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
    
    def _generate_contextual_response(self, user_input: str, competency, response_type: str) -> str:
        """Generate contextual response based on user input and competency"""
        if response_type == "clarification":
            return f"Thank you for sharing that. {competency.response_template} What I'm hearing is that this situation is important to you. Can you help me understand more about what's behind this?"
        else:
            return f"That's really interesting. {competency.response_template} I'm curious about what assumptions or beliefs might be influencing your perspective here."
    
    def _generate_insights(self, state: ConversationState) -> List[str]:
        """Generate insights based on conversation history"""
        # This is a simplified version - in practice, you'd use NLP to analyze patterns
        insights = []
        user_messages = [msg["content"] for msg in state.conversation_history if msg["role"] == "user"]
        
        if len(user_messages) >= 2:
            insights.append("I notice you've mentioned several interconnected challenges.")
            insights.append("There seems to be a pattern around [specific theme] in what you're sharing.")
            insights.append("You appear to have clear awareness of what's not working.")
        
        return insights[:2]  # Return max 2 insights 