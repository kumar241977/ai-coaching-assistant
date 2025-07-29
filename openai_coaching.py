"""
OpenAI-Powered Intelligent Coaching Engine

This module provides sophisticated AI coaching responses using OpenAI's GPT models
while maintaining ICF (International Coaching Federation) competency standards.
"""

import openai
import os
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

# Add current directory to Python path to ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from intelligent_nlp import IntelligentContextAnalyzer, UserContext
    INTELLIGENT_NLP_AVAILABLE = True
    print("✅ INTELLIGENT NLP: Successfully imported")
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔧 Creating enhanced fallback context analyzer...")
    INTELLIGENT_NLP_AVAILABLE = False
    
    # Enhanced fallback implementation with basic intelligence
    @dataclass
    class UserContext:
        corrected_text: str = ""
        primary_emotions: List[str] = None
        challenges_mentioned: List[str] = None
        strengths_mentioned: List[str] = None
        intent: str = "exploring"
        confidence_level: str = "medium"
        readiness_for_action: str = "exploring"
        key_themes: List[str] = None
        sentiment_score: float = 0.0
        
        def __post_init__(self):
            if self.primary_emotions is None:
                self.primary_emotions = []
            if self.challenges_mentioned is None:
                self.challenges_mentioned = []
            if self.strengths_mentioned is None:
                self.strengths_mentioned = []
            if self.key_themes is None:
                self.key_themes = []
    
    class IntelligentContextAnalyzer:
        def __init__(self):
            # Basic spell corrections
            self.corrections = {
                'procastination': 'procrastination',
                'procastinate': 'procrastinate',
                'bigest': 'biggest',
                'chalenge': 'challenge'
            }
        
        def analyze_context(self, user_input: str, conversation_history=None):
            # Basic spell correction
            corrected = user_input
            for wrong, right in self.corrections.items():
                corrected = corrected.replace(wrong, right)
            
            # Basic pattern detection
            text_lower = corrected.lower()
            emotions = []
            challenges = []
            
            if any(word in text_lower for word in ['scared', 'afraid', 'anxious', 'worried']):
                emotions.append('anxiety')
            if any(word in text_lower for word in ['doubt', 'unsure', 'uncertain']):
                emotions.append('doubt')
            if any(word in text_lower for word in ['procrastination', 'procrastinate', 'delay']):
                challenges.append('procrastination')
            if any(word in text_lower for word in ['new task', 'unfamiliar', 'new']):
                challenges.append('new_tasks')
                
            return UserContext(
                corrected_text=corrected,
                primary_emotions=emotions,
                challenges_mentioned=challenges,
                intent='sharing_information',
                confidence_level='low' if emotions else 'medium'
            )
        
        def generate_contextual_response(self, context, depth):
            # Initialize response tracking if not exists
            if not hasattr(self, '_used_contextual_responses'):
                self._used_contextual_responses = set()
            
            # Progressive conversation building based on depth and content
            text_lower = context.corrected_text.lower()
            
            # Build response options for each scenario
            response_options = []
            
            # First response (depth 1-2) - Acknowledge and explore
            if depth <= 2:
                if 'procrastination' in context.challenges_mentioned:
                    if 'biggest' in text_lower:
                        response_options = [
                            "Procrastination being your biggest challenge tells me this is really impacting your effectiveness. What specific situations make it feel most overwhelming?",
                            "I can hear that procrastination feels like a major barrier for you. What happens in the moments just before you decide to postpone a task?",
                            "That sounds like procrastination is creating significant stress in your work life. Can you walk me through what a typical procrastination cycle looks like for you?"
                        ]
                    else:
                        response_options = [
                            "I hear that procrastination is creating real challenges for you. Can you help me understand what procrastination looks like in your day-to-day work?",
                            "Procrastination can feel overwhelming when it becomes a pattern. What types of tasks do you find yourself putting off most often?",
                            "Thank you for sharing that. What do you think triggers your procrastination response most strongly?"
                        ]
                elif any(word in text_lower for word in ['stressed', 'stress', 'confidence', 'confident']):
                    response_options = [
                        "I can hear the stress and confidence challenges you're describing. When you're facing a challenging task, what thoughts typically go through your mind first?",
                        "It sounds like stress and confidence are really interconnected for you. What happens internally when you encounter something that feels difficult?",
                        "I notice you mentioned both stress and confidence - these often feed into each other. What does that experience feel like for you?"
                    ]
                else:
                    response_options = [
                        "Thank you for sharing that. What aspect of this situation feels most urgent for you right now?",
                        "I appreciate you opening up about this. What's the most important thing you'd like me to understand about your experience?",
                        "That gives me a good sense of what you're dealing with. What feels like the biggest challenge in this situation?"
                    ]
            
            # Second response (depth 3-4) - Dig deeper into patterns and impact
            elif depth <= 4:
                if any(word in text_lower for word in ['manager', 'team', 'performance', 'appraisal', 'ratings']):
                    response_options = [
                        "I can hear how this is affecting your professional relationships and reputation. That must feel quite heavy. What's the most difficult part about how others are perceiving your work right now?",
                        "It sounds like this is impacting how you're seen at work, which can feel really vulnerable. What concerns you most about your professional reputation right now?",
                        "The workplace dynamics you're describing sound challenging. How do you think this pattern is affecting your relationships with colleagues and supervisors?"
                    ]
                elif any(word in text_lower for word in ['confidence', 'brand', 'competent', 'leader']):
                    response_options = [
                        "It sounds like this is touching something deeper about your professional identity and how you see yourself as a leader. What would it mean to you to rebuild that confidence?",
                        "I hear how this is affecting your sense of leadership and professional identity. What aspects of your leadership style do you feel have been impacted most?",
                        "Your professional brand and confidence seem really important to you. What version of yourself would you like to reconnect with?",
                        "It seems like your identity as a competent professional is being challenged here. What qualities do you want to reclaim or strengthen?"
                    ]
                elif any(word in text_lower for word in ['challenging', 'tasks', 'unable', 'stressed']):
                    response_options = [
                        "I'm hearing a pattern where challenging tasks trigger stress and avoidance. What do you think is driving that initial stress response when something feels difficult?",
                        "There seems to be a cycle between challenging work and stress for you. When did you first notice this pattern developing?",
                        "It sounds like difficult tasks create a stress response that makes them even harder to tackle. What do you think breaks that cycle for you when it does get broken?"
                    ]
                else:
                    response_options = [
                        "There's clearly a lot beneath the surface here. What feels like the most important piece for us to understand better?",
                        "I can sense there are multiple layers to what you're experiencing. What aspect would you like to explore more deeply?",
                        "It seems like there are several interconnected challenges here. Which one feels most central to address?"
                    ]
            
            # Later responses (depth 5+) - Move toward insight and solutions
            else:
                if any(word in text_lower for word in ['losing', 'going down', 'bad light', 'hesitant']):
                    response_options = [
                        "I can hear how painful this professional decline feels. You're clearly someone who cares deeply about excellence. What strengths do you have that you could lean on to start turning this around?",
                        "The decline you're describing sounds really difficult to experience. What resources or past successes could you draw on to start rebuilding?",
                        "It takes courage to acknowledge when things feel like they're going downhill. What small step could help you start moving in a different direction?"
                    ]
                elif any(word in text_lower for word in ['brand value', 'competent leader', 'reputation']):
                    response_options = [
                        "Your awareness of how this impacts your leadership brand shows real insight. Given everything you've shared, what feels like the most important shift you could make to start rebuilding that reputation?",
                        "I can see how much your professional reputation means to you. What would be the first sign that you're moving back toward the leader you want to be?",
                        "Your leadership brand is clearly important to your identity. What would it look like to start making small changes that align with who you want to be professionally?"
                    ]
                elif 'understand' in text_lower:
                    response_options = [
                        "I can see you're looking for deeper understanding of this pattern. Based on everything you've described - the stress, the avoidance, the impact on your reputation - what do you think might be the root cause driving all of this?",
                        "Your desire to understand this pattern shows real self-awareness. What connections are you starting to make about what might be underneath all of this?",
                        "It sounds like you're ready to look deeper at what's driving these challenges. What insights are beginning to emerge for you?"
                    ]
                else:
                    response_options = [
                        "You've painted a clear picture of how this is affecting multiple areas of your professional life. What feels like the most important insight or shift you'd like to focus on moving forward?",
                        "Given everything you've shared, what feels like the key breakthrough or change that could make the biggest difference?",
                        "You've shown a lot of self-awareness in describing this situation. What action or insight feels most important to focus on next?"
                    ]
            
            # Select an unused response
            available_responses = [r for r in response_options if r not in self._used_contextual_responses]
            
            # If all responses have been used, clear history and use any
            if not available_responses:
                self._used_contextual_responses.clear()
                available_responses = response_options
            
            # Select response (prefer first unused, but randomize if multiple available)
            import random
            chosen_response = random.choice(available_responses) if len(available_responses) > 1 else available_responses[0]
            self._used_contextual_responses.add(chosen_response)
            
            # Keep only recent responses in memory (last 5)
            if len(self._used_contextual_responses) > 5:
                self._used_contextual_responses = set(list(self._used_contextual_responses)[-5:])
            
            return chosen_response

@dataclass
class CoachingContext:
    topic: str
    stage: str
    conversation_history: List[Dict[str, str]]
    user_emotional_state: str
    icf_competency: str
    session_goals: List[str]

class OpenAICoachingEngine:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI coaching engine with intelligent NLP capabilities"""
        # GitHub Models uses GitHub token instead of OpenAI API key
        # Check for provided token, environment variable, or built-in Codespaces token
        self.github_token = api_key or os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
        
        if not self.github_token:
            # For demo purposes, we'll use a placeholder
            self.github_token = "demo-key-replace-with-github-token"
            self.demo_mode = True
            print("🤖 DEMO MODE: Using intelligent NLP responses. Set GITHUB_TOKEN to enable GitHub Models.")
        else:
            self.demo_mode = False
            print("✅ GITHUB MODELS: Using GitHub Models API for intelligent coaching responses.")
            print(f"   Token found: {self.github_token[:7]}...{self.github_token[-4:] if len(self.github_token) > 10 else 'short'}")
        
        # Initialize intelligent context analyzer
        try:
            self.context_analyzer = IntelligentContextAnalyzer()
            if INTELLIGENT_NLP_AVAILABLE:
                print("🧠 FULL INTELLIGENT NLP: Advanced semantic understanding active")
            else:
                print("🔧 ENHANCED FALLBACK: Basic intelligent responses active")
        except Exception as e:
            print(f"⚠️ Context analyzer error: {e}")
            self.context_analyzer = IntelligentContextAnalyzer()
        
        self.icf_competencies = {
            "establishing_trust_and_intimacy": "Create a safe, supportive, and confidential coaching environment. Show genuine care and concern.",
            "active_listening": "Focus completely on what the client is saying. Listen for meaning, emotion, and what's not being said.",
            "powerful_questioning": "Ask questions that reveal underlying assumptions, create greater clarity, and move the client forward.",
            "creating_awareness": "Help the client identify patterns, gain insights, and see new perspectives.",
            "designing_actions": "Partner with the client to create specific, measurable actions that move them toward their goals.",
            "managing_progress_and_accountability": "Hold the client accountable and celebrate their progress."
        }
    
    def generate_coaching_response(self, context: CoachingContext, user_message: str) -> Dict[str, Any]:
        """Generate intelligent coaching response using OpenAI"""
        if self.demo_mode:
            print("🤖 Using DEMO MODE - Enhanced responses with no repetition")
            return self._generate_demo_response(context, user_message)
        
        try:
            print("🔄 Attempting GitHub Models API call...")
            
            # Create conversation messages
            system_prompt = self._create_system_prompt(context)
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history (last 5 messages to stay within limits)
            recent_history = context.conversation_history[-5:] if context.conversation_history else []
            for msg in recent_history:
                messages.append({"role": msg["role"], "content": msg["content"]})
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Generate response using GitHub Models
            from openai import OpenAI
            client = OpenAI(
                base_url="https://models.github.ai/inference",
                api_key=self.github_token
            )
            
            response = client.chat.completions.create(
                model="openai/gpt-4o-mini",  # Using mini model for better availability
                messages=messages,
                max_tokens=300,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            coach_response = response.choices[0].message.content
            
            # Generate follow-up questions
            questions = self._generate_follow_up_questions(context, user_message, coach_response)
            
            print("✅ GitHub Models response generated successfully")
            
            return {
                "message": coach_response,
                "questions": questions,
                "competency_applied": context.icf_competency,
                "confidence": 0.9,
                "suggested_next_stage": self._suggest_next_stage(context, user_message),
                "demo_mode": False
            }
            
        except Exception as e:
            print(f"❌ GitHub Models error: {e}")
            print("🔄 Falling back to enhanced demo mode...")
            return self._generate_demo_response(context, user_message)
    
    def _create_system_prompt(self, context: CoachingContext) -> str:
        """Create system prompt for OpenAI based on ICF competencies and context"""
        competency_guidance = self.icf_competencies.get(context.icf_competency, "")
        
        return f"""You are a professional ICF-certified executive coach conducting a coaching session.

CURRENT CONTEXT:
- Topic: {context.topic}
- Conversation Stage: {context.stage}
- ICF Competency Focus: {context.icf_competency}
- User's Emotional State: {context.user_emotional_state}

ICF COMPETENCY GUIDANCE:
{competency_guidance}

COACHING APPROACH:
- Use powerful, open-ended questions that create awareness
- Listen for underlying beliefs, patterns, and assumptions
- Create a safe, non-judgmental space
- Help the client discover their own insights rather than giving advice
- Be curious, empathetic, and present
- Keep responses concise but meaningful (2-3 sentences max)
- End with a thoughtful question that moves the conversation forward

STAGE-SPECIFIC FOCUS:
{self._get_stage_guidance(context.stage)}

Respond as a skilled coach would - with genuine curiosity, empathy, and powerful questions that help the client gain clarity and move forward."""

    def _get_stage_guidance(self, stage: str) -> str:
        """Get stage-specific coaching guidance"""
        stage_guidance = {
            "intake": "Focus on understanding what the client wants to work on. Create safety and establish the coaching relationship.",
            "exploration": "Help the client explore the situation deeply. Listen for patterns, emotions, and underlying beliefs.",
            "reflection": "Help the client gain insights and awareness. Point out patterns and help them see new perspectives.", 
            "action_planning": "Partner with the client to create specific, actionable steps. Focus on commitment and accountability.",
            "follow_up": "Review progress, celebrate successes, and adjust plans as needed."
        }
        return stage_guidance.get(stage, "Focus on the client's needs and help them move forward.")
    
    def _generate_follow_up_questions(self, context: CoachingContext, user_message: str, coach_response: str) -> List[str]:
        """Generate relevant follow-up questions"""
        if self.demo_mode:
            return self._get_demo_questions(context.stage, context.topic)
        
        # In a real implementation, you could use another OpenAI call to generate questions
        # For now, return contextual questions based on stage and topic
        return self._get_contextual_questions(context.stage, context.topic, user_message)
    
    def _get_contextual_questions(self, stage: str, topic: str, user_message: str) -> List[str]:
        """Get contextual questions based on stage and topic"""
        questions = {
            "exploration": [
                "What else is important about this situation?",
                "How does this impact other areas of your life?",
                "What would need to change for this to improve?"
            ],
            "reflection": [
                "What patterns do you notice here?",
                "What insights are emerging for you?",
                "How does this align with your values?"
            ],
            "action_planning": [
                "What specific action feels most important right now?",
                "What support do you need to make this happen?",
                "How will you know you're successful?"
            ],
            "follow_up": [
                "How has your action plan been working for you?",
                "What progress have you made since our last conversation?",
                "What adjustments do you need to make to your approach?",
                "What additional support would be helpful moving forward?",
                "How will you maintain momentum on this growth area?"
            ]
        }
        return questions.get(stage, ["Tell me more about that.", "What's most important here?"])
    
    def _suggest_next_stage(self, context: CoachingContext, user_message: str) -> str:
        """Intelligently suggest next stage based on conversation content and progress"""
        current_stage = context.stage
        conversation_depth = len(context.conversation_history)
        user_lower = user_message.lower()
        
        # Content-based stage progression (more intelligent than just depth)
        if current_stage == "exploration":
            # Move to reflection when user shows self-awareness or insight
            insight_indicators = [
                "i notice", "i realize", "i see that", "i understand", "it's because",
                "the pattern", "what drives this", "i think it's", "maybe it's",
                "i'm starting to see", "now i understand", "it seems like", "i believe"
            ]
            
            if any(indicator in user_lower for indicator in insight_indicators) or conversation_depth >= 5:
                return "reflection"
                
        elif current_stage == "reflection":
            # Move to action planning when user expresses readiness or desire for change
            action_indicators = [
                "i want to", "i need to", "i should", "what should i do", "how do i",
                "what's the next step", "i'm ready", "i want to change", "help me",
                "what can i do", "i'd like to try", "how can i", "that's exactly why",
                "yes", "absolutely", "let's do it", "i'm ready", "ready to create",
                "action plan", "let's create", "ready for action", "move forward",
                "take action", "next step", "what should i do"
            ]
            
            if any(indicator in user_lower for indicator in action_indicators) or conversation_depth >= 7:
                return "action_planning"
                
        elif current_stage == "action_planning":
            # Move to follow-up when user has committed to specific actions
            commitment_indicators = [
                "i will", "i'll try", "i commit", "i'm going to", "my goal is",
                "i'll start", "i'll work on", "i'll practice", "i'll focus on",
                "as a first step", "i want to not", "if i take", "my plan is",
                "i'll implement", "i'll apply", "i'll begin", "starting this week",
                "my action", "i plan to", "i intend to", "i want to pick up",
                "stretch project", "try my hands", "i want to take on"
            ]
            
            if any(indicator in user_lower for indicator in commitment_indicators) or conversation_depth >= 9:
                return "follow_up"
        
        return current_stage
    
    def reset_conversation_state(self):
        """Reset conversation state for new coaching session"""
        if hasattr(self, '_conversation_questions_used'):
            self._conversation_questions_used.clear()
        if hasattr(self, '_used_responses'):
            self._used_responses.clear()
        if hasattr(self, '_used_action_responses'):
            self._used_action_responses.clear()
        if hasattr(self, '_used_followup_responses'):
            self._used_followup_responses.clear()
        if hasattr(self.context_analyzer, '_used_contextual_responses'):
            self.context_analyzer._used_contextual_responses.clear()
        print("🔄 Conversation state reset for new coaching session")
    
    def _generate_demo_response(self, context: CoachingContext, user_message: str) -> Dict[str, Any]:
        """Generate demo responses when OpenAI API is not available"""
        user_lower = user_message.lower()
        conversation_depth = len(context.conversation_history)
        current_stage = context.stage
        
        # Track used responses to avoid repetition
        if not hasattr(self, '_used_responses'):
            self._used_responses = set()

        # Handle follow-up stage specifically
        if current_stage == "follow_up":
            responses = [
                "I'm so glad to connect with you again! It's wonderful that you've taken steps toward your growth mindset goal. What has been your experience since we last talked?",
                "Welcome back! I'm curious to hear how things have been going with developing that growth mindset approach to challenges. What have you noticed about yourself?",
                "It's great to see you again! I'd love to hear about your journey with embracing challenges as growth opportunities. What's been happening for you?",
                "Thank you for coming back to continue this important work. How has your relationship with new challenges evolved since our last session?",
                "I'm excited to hear about your progress! What shifts have you noticed in how you approach difficult or unfamiliar tasks?"
            ]
            response = self._get_unused_response(responses)
            
            return {
                "message": response,
                "questions": self._get_varied_demo_questions(context.stage, conversation_depth, user_message),
                "competency_applied": context.icf_competency,
                "confidence": 0.8,
                "suggested_next_stage": "follow_up",
                "demo_mode": True
            }

        # Generate truly contextual responses based on semantic understanding
        response = self._generate_contextual_response(user_message, conversation_depth, context)

        return {
            "message": response,
            "questions": self._get_intelligent_questions(user_message, context.stage, conversation_depth),
            "competency_applied": context.icf_competency,
            "confidence": 0.8,
            "suggested_next_stage": self._suggest_next_stage(context, user_message),
            "demo_mode": True
        }
    
    def _get_unused_response(self, response_options: List[str]) -> str:
        """Get a response that hasn't been used recently"""
        import random
        
        # Filter out recently used responses
        available_responses = [r for r in response_options if r not in self._used_responses]
        
        # If all responses have been used, clear the history and use any
        if not available_responses:
            self._used_responses.clear()
            available_responses = response_options
        
        # Select a random unused response
        chosen_response = random.choice(available_responses)
        self._used_responses.add(chosen_response)
        
        # Keep only recent responses in memory (last 3)
        if len(self._used_responses) > 3:
            self._used_responses = set(list(self._used_responses)[-3:])
        
        return chosen_response
    
    def _get_varied_demo_questions(self, stage: str, conversation_depth: int, user_message: str = "") -> List[str]:
        """Get truly adaptive follow-up questions that build on conversation"""
        import random
        
        # Track ALL used questions for this conversation (never repeat)
        if not hasattr(self, '_conversation_questions_used'):
            self._conversation_questions_used = set()
        
        user_lower = user_message.lower() if user_message else ""
        
        # Create comprehensive question pool organized by purpose
        question_bank = {
            # Exploration & Understanding
            "exploration": [
                "What beliefs about yourself might be contributing to this situation?",
                "What thoughts go through your mind when facing these situations?",
                "What physical sensations do you notice when this happens?",
                "What stories do you tell yourself in these moments?",
                "What would your best friend say about this situation?",
                "What's underneath this challenge for you?",
                "What does this situation remind you of from your past?",
                "What are you learning about yourself through this?",
                "What assumptions might you be making here?",
                "What's the most surprising thing about this pattern?"
            ],
            
            # Patterns & Awareness
            "patterns": [
                "What patterns do you notice about when this happens most?",
                "When you do feel confident and capable, what's different?",
                "What circumstances tend to trigger this response?",
                "How does this show up in other areas of your life?",
                "What would need to be different for you to feel more confident?",
                "What environments or situations bring out your best?",
                "What's worked for you in similar situations before?",
                "What would someone who knows you well say about your strengths?",
                "How has this pattern served you in the past?",
                "What's changed recently that might be affecting this?"
            ],
            
            # Resources & Strengths
            "resources": [
                "What resources or support systems do you currently have?",
                "What skills do you already possess that could help here?",
                "Who in your life believes in your capabilities?",
                "What past successes can you draw strength from?",
                "What would accessing your full potential look like?",
                "What support would be most helpful right now?",
                "What internal resources can you tap into?",
                "What would encourage you to take the next step?",
                "What would your wisest self advise you to do?",
                "What energizes you most about making this change?"
            ],
            
            # Action & Implementation
            "action": [
                "What feels like the most natural first step for you?",
                "What small experiment could you try this week?",
                "What would make taking action feel easier?",
                "What obstacles do you anticipate, and how might you address them?",
                "What would accountability look like for you?",
                "What would motivate you to follow through?",
                "How could you break this down into smaller pieces?",
                "What would you need to believe about yourself to move forward?",
                "What would happen if you trusted yourself more?",
                "What commitment are you ready to make to yourself?"
            ],
            
            # Success & Vision
            "success": [
                "What would it feel like to have overcome this challenge?",
                "How would others notice the change in you?",
                "What would become possible if you solved this?",
                "What impact would this change have on your work/life?",
                "What legacy do you want to create around this?",
                "How will you celebrate when you make progress?",
                "What would your future self thank you for doing now?",
                "What excites you most about this potential change?",
                "What would confidence look like in your daily life?",
                "How would you know you're making real progress?"
            ],
            
            # Context-specific questions based on user content
            "procrastination": [
                "What typically happens right before you decide to postpone a task?",
                "How long do tasks usually sit before you finally tackle them?",
                "What's the difference between tasks you complete immediately vs. those you postpone?"
            ],
            
            "confidence": [
                "When was the last time you felt truly confident in your abilities?",
                "What would need to happen for you to trust yourself more with new challenges?",
                "How do you typically build confidence when learning something new?"
            ],
            
            "new_tasks": [
                "What makes a task feel 'manageable' vs. 'overwhelming' to you?",
                "How do you usually approach learning something completely new?",
                "What support would help you feel more prepared for unfamiliar work?"
            ]
        }
        
        # Determine question categories based on user content and conversation stage
        primary_categories = []
        secondary_categories = []
        
        # Add context-specific categories based on user's message
        if "procrastination" in user_lower or "procrastinate" in user_lower:
            primary_categories.append("procrastination")
        if "confidence" in user_lower or "doubt" in user_lower:
            primary_categories.append("confidence")  
        if "new task" in user_lower or "unfamiliar" in user_lower:
            primary_categories.append("new_tasks")
            
        # Standard categories based on conversation depth
        if conversation_depth <= 2:
            primary_categories.extend(["exploration", "patterns"])
            secondary_categories = ["resources"]
        elif conversation_depth <= 4:
            primary_categories.extend(["patterns", "resources"])
            secondary_categories = ["exploration", "action"]
        else:
            primary_categories.extend(["action", "success"])
            secondary_categories = ["resources", "patterns"]
        
        # Collect available questions from relevant categories
        candidate_questions = []
        
        # Add primary category questions
        for category in primary_categories:
            if category in question_bank:
                candidate_questions.extend(question_bank[category])
        
        # Add some secondary category questions for variety
        for category in secondary_categories:
            if category in question_bank:
                candidate_questions.extend(question_bank[category][:3])
        
        # Filter out questions already used in this conversation
        available_questions = [q for q in candidate_questions if q not in self._conversation_questions_used]
        
        # If we've somehow exhausted questions
        if len(available_questions) < 2:
            self._conversation_questions_used.clear()
            available_questions = [
                "What insight feels most important right now?",
                "What would you like to explore further?",
                "What's calling for your attention in this situation?"
            ]
        
        # Select 2 diverse questions
        selected_questions = random.sample(available_questions, min(2, len(available_questions)))
        
        # Mark as used
        self._conversation_questions_used.update(selected_questions)
        
        return selected_questions
        
    def _get_intelligent_questions(self, user_message: str, stage: str, conversation_depth: int) -> List[str]:
        """Generate progressive, contextual questions that build on the conversation"""
        
        # Use the sophisticated question tracking system from _get_varied_demo_questions
        return self._get_varied_demo_questions(stage, conversation_depth, user_message)

    def _generate_contextual_response(self, user_message: str, conversation_depth: int, context: CoachingContext) -> str:
        """Generate intelligent responses using semantic understanding"""
        
        # Use intelligent context analyzer for deep understanding
        user_context = self.context_analyzer.analyze_context(
            user_message, 
            context.conversation_history
        )
        
        # Debug output showing intelligent analysis
        print(f"🧠 INTELLIGENT ANALYSIS:")
        print(f"   Original: '{user_message}'")
        print(f"   Corrected: '{user_context.corrected_text}'")
        print(f"   Intent: {user_context.intent}")
        print(f"   Emotions: {user_context.primary_emotions}")
        print(f"   Challenges: {user_context.challenges_mentioned}")
        print(f"   Strengths: {user_context.strengths_mentioned}")
        print(f"   Confidence: {user_context.confidence_level}")
        print(f"   Readiness: {user_context.readiness_for_action}")
        print(f"   Themes: {user_context.key_themes}")
        print(f"   Sentiment: {user_context.sentiment_score}")
        print(f"   Current Stage: {context.stage}")
        
        # Check if we're in action planning or follow-up stage and provide stage-specific responses
        if context.stage == "action_planning":
            response = self._generate_action_planning_response_text(user_context, conversation_depth, user_message)
        elif context.stage == "follow_up":
            response = self._generate_follow_up_response_text(user_context, conversation_depth, user_message)
        else:
            # Generate response using intelligent understanding for exploration/reflection stages
            response = self.context_analyzer.generate_contextual_response(user_context, conversation_depth)
        
        return response
    
    def _generate_action_planning_response_text(self, user_context, conversation_depth: int, user_message: str) -> str:
        """Generate action planning stage specific responses with tracking"""
        if not hasattr(self, '_used_action_responses'):
            self._used_action_responses = set()
        
        text_lower = user_message.lower()
        
        # Action planning focused response options
        if any(word in text_lower for word in ['ready', 'action plan', 'want to', 'commit', 'yes']):
            response_options = [
                "That's wonderful to hear your readiness! What specific action feels most important to focus on first?",
                "I can sense your commitment to moving forward. What would be the most meaningful first step you could take?",
                "Your willingness to take action is inspiring. What concrete step could you commit to this week?",
                "I appreciate your readiness to create change. What action would have the biggest impact on your situation?"
            ]
        elif any(word in text_lower for word in ['break down', 'smaller', 'steps', 'plan']):
            response_options = [
                "Breaking things down into smaller steps is such a powerful strategy! How might you structure these smaller tasks?",
                "That approach of breaking complex tasks down shows real insight. What would be your first small step?",
                "I love how you're thinking about manageable pieces. What's the smallest step you could take to get started?",
                "Your plan to break things down is excellent. How will you organize these smaller tasks to maintain momentum?"
            ]
        elif any(word in text_lower for word in ['fear', 'scared', 'overcome', 'challenge']):
            response_options = [
                "Moving through fear takes real courage. What support would help you take that first brave step?",
                "I hear your determination to overcome these challenges. What would make the first action feel more manageable?",
                "Your awareness of fear is the first step to moving through it. What would help you feel more prepared?",
                "It takes strength to face fears head-on. What resources could you tap into to support this change?"
            ]
        elif any(word in text_lower for word in ['stretch', 'project', 'try', 'hands on']):
            response_options = [
                "A stretch project sounds like a perfect way to put your new approach into practice! What type of project are you considering?",
                "I love that you want to challenge yourself with something new. What would make this stretch project feel both challenging and achievable?",
                "Taking on a stretch project shows real growth mindset. How will you approach this differently than you might have before?",
                "What an excellent way to practice your new skills! What support would help you succeed with this stretch project?"
            ]
        else:
            # General action planning responses
            response_options = [
                "Let's focus on turning your insights into action. What specific change would make the biggest difference?",
                "I can see you're ready to move forward. What concrete step feels most important to commit to?",
                "Your self-awareness gives you a strong foundation for action. What would you like to focus on implementing?",
                "What action could you take that would start to shift the patterns we've been discussing?",
                "How can we translate your insights into specific, actionable steps?",
                "What would be the most meaningful action you could commit to right now?"
            ]
        
        # Select unused response
        available_responses = [r for r in response_options if r not in self._used_action_responses]
        if not available_responses:
            self._used_action_responses.clear()
            available_responses = response_options
        
        import random
        chosen_response = random.choice(available_responses)
        self._used_action_responses.add(chosen_response)
        
        # Keep only recent responses in memory
        if len(self._used_action_responses) > 4:
            self._used_action_responses = set(list(self._used_action_responses)[-4:])
        
        return chosen_response
    
    def _generate_follow_up_response_text(self, user_context, conversation_depth: int, user_message: str) -> str:
        """Generate follow-up stage specific responses with tracking"""
        if not hasattr(self, '_used_followup_responses'):
            self._used_followup_responses = set()
        
        text_lower = user_message.lower()
        
        # Follow-up focused response options
        if any(word in text_lower for word in ['progress', 'better', 'working', 'success']):
            response_options = [
                "That's fantastic progress! What has been the most surprising part of your journey so far?",
                "I'm thrilled to hear about your success! What's been the key to making this progress?",
                "Your progress is inspiring! What difference are you noticing in how you approach challenges now?",
                "It's wonderful to see your hard work paying off. What would you like to build on next?"
            ]
        elif any(word in text_lower for word in ['struggle', 'difficult', 'challenge', 'hard']):
            response_options = [
                "Thank you for being honest about the challenges. What support would be most helpful right now?",
                "I appreciate you sharing what's been difficult. What adjustments might help you move forward?",
                "It takes courage to acknowledge when things are tough. What have you learned about yourself through these challenges?",
                "Struggles are part of the growth process. What strengths can you draw on to navigate this?"
            ]
        elif any(word in text_lower for word in ['maintain', 'continue', 'momentum', 'keep going']):
            response_options = [
                "Maintaining momentum is so important! What systems are helping you stay consistent?",
                "I love your focus on sustainability. What's working best to keep you motivated?",
                "Your commitment to continuous progress is admirable. How are you celebrating your wins along the way?",
                "Consistency is key to lasting change. What habits are you building to support your growth?"
            ]
        else:
            # General follow-up responses
            response_options = [
                "It's great to reconnect and hear about your journey. What's been most significant for you since we last talked?",
                "I'm curious to learn about your experience. What insights have emerged as you've been implementing changes?",
                "Thank you for sharing your progress. What feels most important to focus on as you continue growing?",
                "I appreciate you taking time to reflect on your growth. What would be most helpful to explore today?",
                "Your continued commitment to growth is inspiring. What's calling for your attention right now?"
            ]
        
        # Select unused response
        available_responses = [r for r in response_options if r not in self._used_followup_responses]
        if not available_responses:
            self._used_followup_responses.clear()
            available_responses = response_options
        
        import random
        chosen_response = random.choice(available_responses)
        self._used_followup_responses.add(chosen_response)
        
        # Keep only recent responses in memory
        if len(self._used_followup_responses) > 4:
            self._used_followup_responses = set(list(self._used_followup_responses)[-4:])
        
        return chosen_response
            
    def _generate_fallback_response(self, context: CoachingContext, user_message: str) -> Dict[str, Any]:
        """Generate fallback response when OpenAI fails"""
        return {
            "message": "I appreciate you sharing that with me. This seems really important to you. Can you help me understand what aspect of this situation you'd most like to explore?",
            "questions": ["What feels most urgent about this?", "What would success look like?"],
            "competency_applied": context.icf_competency,
            "confidence": 0.6,
            "suggested_next_stage": context.stage
        } 