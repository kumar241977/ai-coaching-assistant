"""
Intelligent Context Analyzer for Coaching (Lightweight Version)

This module provides intelligent natural language understanding without requiring
additional dependencies beyond standard Python libraries.
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class UserContext:
    """Represents the understood context from user input"""
    corrected_text: str
    primary_emotions: List[str]
    challenges_mentioned: List[str]
    strengths_mentioned: List[str]
    intent: str  # what the user is trying to achieve
    confidence_level: str  # high, medium, low
    readiness_for_action: str  # ready, exploring, resistant
    key_themes: List[str]
    sentiment_score: float  # -1 to 1

class IntelligentContextAnalyzer:
    """Analyzes user input for semantic meaning and context using lightweight processing"""
    
    def __init__(self):
        # Common spelling corrections for coaching terms
        self.spelling_corrections = {
            'procastination': 'procrastination',
            'procastinate': 'procrastinate',
            'procastinating': 'procrastinating',
            'sucessfully': 'successfully',
            'sucessful': 'successful',
            'chalenge': 'challenge',
            'chalenges': 'challenges',
            'bigest': 'biggest',
            'strenghts': 'strengths',
            'strenght': 'strength',
            'confidance': 'confidence',
            'overwheled': 'overwhelmed',
            'perfomance': 'performance',
            'experiance': 'experience',
            'responsability': 'responsibility'
        }
        
        self.emotion_patterns = {
            'anxiety': ['scared', 'afraid', 'anxious', 'worried', 'nervous', 'jittery', 'fearful', 'stressed', 'terrified'],
            'doubt': ['doubt', 'uncertain', 'unsure', 'questioning', 'hesitant', 'skeptical', 'confused'],
            'frustration': ['frustrated', 'annoyed', 'irritated', 'stuck', 'blocked', 'angry', 'upset'],
            'confidence': ['confident', 'sure', 'certain', 'capable', 'skilled', 'competent', 'able'],
            'motivation': ['motivated', 'driven', 'determined', 'committed', 'ready', 'eager', 'excited']
        }
        
        self.challenge_patterns = {
            'procrastination': ['procrastin', 'delay', 'postpone', 'avoid', 'put off', 'stall', 'defer'],
            'confidence_issues': ['self-doubt', 'imposter', 'not good enough', 'inadequate', 'insecure', 'doubt myself'],
            'new_tasks': ['new task', 'unfamiliar', 'unknown', 'never done', 'first time', 'learning', 'new to'],
            'overwhelm': ['overwhelm', 'too much', 'overload', 'stress', 'burden', 'pressure', 'swamped'],
            'perfectionism': ['perfect', 'flawless', 'exactly right', 'mistake', 'failure', 'wrong', 'error']
        }
        
        self.strength_patterns = {
            'execution': ['execution', 'deliver', 'complete', 'finish', 'accomplish', 'achieve', 'get things done'],
            'analytical': ['analyze', 'think', 'logical', 'systematic', 'methodical', 'structured', 'organized'],
            'leadership': ['lead', 'guide', 'manage', 'influence', 'inspire', 'motivate', 'direct'],
            'creativity': ['creative', 'innovative', 'imaginative', 'original', 'artistic', 'inventive'],
            'communication': ['communicate', 'explain', 'present', 'articulate', 'express', 'speak', 'write']
        }
    
    def correct_spelling(self, text: str) -> str:
        """Correct common spelling mistakes"""
        corrected = text
        for wrong, correct in self.spelling_corrections.items():
            # Use word boundaries to avoid partial matches
            corrected = re.sub(r'\b' + re.escape(wrong) + r'\b', correct, corrected, flags=re.IGNORECASE)
        return corrected
    
    def analyze_context(self, user_input: str, conversation_history: List[Dict] = None) -> UserContext:
        """Analyze user input for comprehensive context understanding"""
        
        # Step 1: Correct spelling
        corrected_text = self.correct_spelling(user_input)
        
        # Step 2: Analyze sentiment (simple approach)
        sentiment_score = self._simple_sentiment_analysis(corrected_text)
        
        # Step 3: Extract emotions using semantic patterns
        emotions = self._extract_emotions(corrected_text)
        
        # Step 4: Identify challenges
        challenges = self._extract_challenges(corrected_text)
        
        # Step 5: Identify strengths
        strengths = self._extract_strengths(corrected_text)
        
        # Step 6: Determine user intent
        intent = self._determine_intent(corrected_text, conversation_history)
        
        # Step 7: Assess confidence level
        confidence_level = self._assess_confidence(corrected_text, emotions)
        
        # Step 8: Determine readiness for action
        readiness = self._assess_readiness(corrected_text, intent)
        
        # Step 9: Extract key themes
        themes = self._extract_themes(corrected_text, challenges, strengths, emotions)
        
        return UserContext(
            corrected_text=corrected_text,
            primary_emotions=emotions,
            challenges_mentioned=challenges,
            strengths_mentioned=strengths,
            intent=intent,
            confidence_level=confidence_level,
            readiness_for_action=readiness,
            key_themes=themes,
            sentiment_score=sentiment_score
        )
    
    def _simple_sentiment_analysis(self, text: str) -> float:
        """Simple sentiment analysis using word lists"""
        positive_words = ['good', 'great', 'excellent', 'confident', 'capable', 'ready', 'excited', 'motivated', 'strong', 'successful']
        negative_words = ['bad', 'terrible', 'awful', 'scared', 'worried', 'anxious', 'frustrated', 'stuck', 'failed', 'overwhelmed']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.0
            
        # Simple sentiment score between -1 and 1
        sentiment = (positive_count - negative_count) / max(total_words, 1)
        return max(-1.0, min(1.0, sentiment * 2))  # Scale and clamp
    
    def _extract_emotions(self, text: str) -> List[str]:
        """Extract emotions from text using pattern matching"""
        text_lower = text.lower()
        detected_emotions = []
        
        for emotion, patterns in self.emotion_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                detected_emotions.append(emotion)
        
        # Additional emotional context clues
        if any(word in text_lower for word in ["can't", 'unable', 'difficult', 'hard', 'struggle', 'challenging']):
            if 'difficulty' not in detected_emotions:
                detected_emotions.append('difficulty')
        
        if any(phrase in text_lower for phrase in ['want to', 'need to', 'have to', 'should', 'ready to']):
            if 'motivation' not in detected_emotions:
                detected_emotions.append('motivation')
                
        return detected_emotions[:3]  # Return top 3 emotions
    
    def _extract_challenges(self, text: str) -> List[str]:
        """Extract challenges from text using pattern matching"""
        text_lower = text.lower()
        detected_challenges = []
        
        for challenge, patterns in self.challenge_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                detected_challenges.append(challenge)
        
        return detected_challenges
    
    def _extract_strengths(self, text: str) -> List[str]:
        """Extract strengths from text using pattern matching"""
        text_lower = text.lower()
        detected_strengths = []
        
        for strength, patterns in self.strength_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                detected_strengths.append(strength)
        
        # Look for positive self-references
        if any(phrase in text_lower for phrase in ['good at', 'excel at', 'strength', 'capable of', 'skilled in']):
            if 'self_awareness' not in detected_strengths:
                detected_strengths.append('self_awareness')
                
        return detected_strengths
    
    def _determine_intent(self, text: str, conversation_history: List[Dict] = None) -> str:
        """Determine what the user is trying to achieve"""
        text_lower = text.lower()
        
        # Intent patterns with more comprehensive matching
        understanding_words = ['understand', 'why', 'reason', 'cause', 'behind', 'what drives', 'what makes']
        solution_words = ['how', 'what can i do', 'help me', 'solution', 'fix', 'resolve', 'overcome']
        action_words = ['want to change', 'ready to', 'commit', 'action', 'will do', 'plan to']
        sharing_words = ['explain', 'describe', 'tell you', 'share', 'let me tell you']
        feeling_words = ['feel', 'think', 'believe', 'sense', 'experience']
        
        if any(word in text_lower for word in understanding_words):
            return 'seeking_understanding'
        elif any(word in text_lower for word in solution_words):
            return 'seeking_solutions'
        elif any(word in text_lower for word in action_words):
            return 'ready_for_action'
        elif any(word in text_lower for word in sharing_words):
            return 'sharing_information'
        elif any(word in text_lower for word in feeling_words):
            return 'expressing_feelings'
        else:
            return 'exploring'
    
    def _assess_confidence(self, text: str, emotions: List[str]) -> str:
        """Assess user's confidence level"""
        text_lower = text.lower()
        
        high_confidence_words = ['confident', 'sure', 'capable', 'skilled', 'good at', 'excel', 'strong']
        low_confidence_words = ['doubt', 'unsure', 'scared', 'anxious', 'worried', 'uncertain', 'insecure']
        
        high_count = sum(1 for word in high_confidence_words if word in text_lower)
        low_count = sum(1 for word in low_confidence_words if word in text_lower)
        
        if any(emotion in emotions for emotion in ['anxiety', 'doubt', 'difficulty']) or low_count > high_count:
            return 'low'
        elif 'confidence' in emotions or high_count > low_count:
            return 'high'
        else:
            return 'medium'
    
    def _assess_readiness(self, text: str, intent: str) -> str:
        """Assess readiness for taking action"""
        text_lower = text.lower()
        
        ready_words = ['ready', 'want to', 'will', 'commit', 'action', 'do', 'change', 'start', 'begin']
        resistant_words = ['but', 'however', 'difficult', "can't", 'unable', 'not sure', 'maybe']
        
        ready_count = sum(1 for word in ready_words if word in text_lower)
        resistant_count = sum(1 for word in resistant_words if word in text_lower)
        
        if intent == 'ready_for_action' or ready_count > resistant_count:
            return 'ready'
        elif resistant_count > ready_count:
            return 'resistant'
        else:
            return 'exploring'
    
    def _extract_themes(self, text: str, challenges: List[str], strengths: List[str], emotions: List[str]) -> List[str]:
        """Extract overarching themes from the conversation"""
        themes = []
        
        # Theme identification based on combinations
        if 'procrastination' in challenges and any(emotion in emotions for emotion in ['anxiety', 'doubt']):
            themes.append('fear_based_avoidance')
        
        if 'new_tasks' in challenges and 'doubt' in emotions:
            themes.append('comfort_zone_resistance')
            
        if 'confidence_issues' in challenges or any(emotion in emotions for emotion in ['doubt', 'anxiety']):
            themes.append('self_worth_concerns')
            
        if any(strength in strengths for strength in ['execution', 'analytical']) and challenges:
            themes.append('capability_awareness_gap')
            
        # Add general themes
        if any(emotion in emotions for emotion in ['anxiety', 'doubt', 'frustration', 'difficulty']):
            themes.append('emotional_barriers')
        
        if challenges:
            themes.append('growth_opportunities')
            
        return themes[:3]  # Return top 3 themes

    def generate_contextual_response(self, context: UserContext, conversation_depth: int) -> str:
        """Generate intelligent responses based on context understanding"""
        
        # Use the analyzed context to create truly contextual responses
        if context.intent == 'seeking_understanding':
            if 'fear_based_avoidance' in context.key_themes:
                challenges_text = ', '.join(context.challenges_mentioned) if context.challenges_mentioned else 'this pattern'
                emotions_text = ', '.join(context.primary_emotions) if context.primary_emotions else 'uncertainty'
                return f"I can hear your genuine desire to understand what's driving this pattern. You've shared about {challenges_text} and I sense the {emotions_text} that comes with it. Often when we avoid things, our mind is trying to protect us from something. What do you think your mind might be trying to shield you from?"
                
        elif context.intent == 'sharing_information':
            if context.confidence_level == 'low' and 'new_tasks' in context.challenges_mentioned:
                challenges_text = ', '.join(context.challenges_mentioned) if context.challenges_mentioned else 'unfamiliar situations'
                emotions_text = ', '.join(context.primary_emotions) if context.primary_emotions else 'uncertainty'
                return f"Thank you for sharing that with me. I can hear how {challenges_text} trigger {emotions_text} for you. It takes courage to acknowledge these feelings. When you're facing something new and that {context.primary_emotions[0] if context.primary_emotions else 'uncertainty'} kicks in, what thoughts tend to go through your mind?"
        
        elif context.readiness_for_action == 'ready':
            challenges_text = ', '.join(context.challenges_mentioned) if context.challenges_mentioned else 'these areas'
            return f"I can sense your readiness to work on this. You've identified {challenges_text} as areas for growth, and that self-awareness is powerful. Given what you've shared, what feels like the most important first step you could take?"
        
        # Fallback based on overall sentiment and themes
        if context.sentiment_score < -0.2:  # Negative sentiment
            themes_text = ', '.join(context.key_themes) if context.key_themes else 'these challenges'
            return f"I can hear the difficulty in what you're experiencing. The {themes_text} you're describing are real challenges that many people face. What feels most important for you to understand about this situation right now?"
        elif context.sentiment_score > 0.2:  # Positive sentiment
            challenges_text = ', '.join(context.challenges_mentioned) if context.challenges_mentioned else 'this situation'
            return f"There's something hopeful in what you're sharing. Even as you describe {challenges_text}, I sense your {context.readiness_for_action} to engage with this. What possibilities do you see ahead?"
        else:  # Neutral
            themes_text = ', '.join(context.key_themes) if context.key_themes else 'what you\'re experiencing'
            return f"I'm listening carefully to what you're sharing about {themes_text}. What stands out most to you as we explore this together?" 