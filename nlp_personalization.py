from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import json
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import sqlite3

@dataclass
class EmotionalTone:
    sentiment: str  # positive, negative, neutral
    intensity: float  # -1 to 1
    emotions: Dict[str, float]  # specific emotions detected
    confidence: float  # confidence in the analysis

@dataclass
class UserProfile:
    user_id: str
    communication_style: str  # direct, supportive, challenging, etc.
    preferred_pace: str  # fast, moderate, slow
    emotional_sensitivity: str  # high, medium, low
    learning_style: str  # visual, auditory, kinesthetic, reading
    session_history: List[Dict[str, Any]]

class EmotionalToneAnalyzer:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.emotion_keywords = self._initialize_emotion_keywords()
    
    def _initialize_emotion_keywords(self) -> Dict[str, List[str]]:
        return {
            "anxiety": ["worried", "nervous", "anxious", "stressed", "overwhelmed", "panic", "fear"],
            "frustration": ["frustrated", "annoyed", "irritated", "stuck", "blocked", "impossible"],
            "excitement": ["excited", "thrilled", "enthusiastic", "motivated", "energized", "pumped"],
            "confusion": ["confused", "unclear", "lost", "don't understand", "mixed up", "puzzled"],
            "confidence": ["confident", "sure", "certain", "capable", "strong", "ready"],
            "sadness": ["sad", "disappointed", "down", "discouraged", "hopeless", "defeated"],
            "hope": ["hopeful", "optimistic", "positive", "better", "improving", "progress"],
            "anger": ["angry", "mad", "furious", "upset", "outraged", "livid"]
        }
    
    def analyze_tone(self, text: str) -> EmotionalTone:
        """Analyze emotional tone of user input"""
        # Use VADER for overall sentiment
        vader_scores = self.vader_analyzer.polarity_scores(text.lower())
        
        # Use TextBlob for additional sentiment analysis
        blob = TextBlob(text)
        textblob_sentiment = blob.sentiment.polarity
        
        # Combine both scores
        combined_sentiment = (vader_scores['compound'] + textblob_sentiment) / 2
        
        # Determine sentiment category
        if combined_sentiment >= 0.1:
            sentiment = "positive"
        elif combined_sentiment <= -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # Detect specific emotions
        emotions = self._detect_emotions(text.lower())
        
        # Calculate confidence based on intensity
        confidence = abs(combined_sentiment)
        
        return EmotionalTone(
            sentiment=sentiment,
            intensity=combined_sentiment,
            emotions=emotions,
            confidence=confidence
        )
    
    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """Detect specific emotions in text"""
        emotions = {}
        text_words = text.split()
        
        for emotion, keywords in self.emotion_keywords.items():
            emotion_score = 0
            for keyword in keywords:
                if keyword in text:
                    emotion_score += 1
            
            # Normalize score
            emotions[emotion] = min(emotion_score / len(keywords), 1.0)
        
        return emotions

class PersonalizationEngine:
    def __init__(self):
        self.user_profiles = {}
        self.response_templates = self._initialize_response_templates()
    
    def _initialize_response_templates(self) -> Dict[str, Dict[str, str]]:
        return {
            "supportive": {
                "high_anxiety": "I can sense this feels overwhelming right now. Let's take this one step at a time.",
                "frustration": "It sounds like this has been really challenging for you. Your frustration is completely understandable.",
                "low_confidence": "I hear some uncertainty in what you're sharing. What would help you feel more confident about this?",
                "excitement": "I can feel your energy and enthusiasm! This excitement can be a powerful resource.",
                "default": ""  # Empty to avoid interference with OpenAI responses
            },
            "challenging": {
                "high_anxiety": "What would happen if you approached this with curiosity rather than worry?",
                "frustration": "What assumptions might be contributing to this frustration?",
                "low_confidence": "What evidence do you have that contradicts this doubt?",
                "excitement": "How can you channel this excitement into focused action?",
                "default": ""  # Empty to avoid interference with OpenAI responses
            },
            "direct": {
                "high_anxiety": "Let's focus on what you can control right now.",
                "frustration": "What specific action will move you forward?",
                "low_confidence": "What's the smallest step you could take today?",
                "excitement": "What's your next concrete step?",
                "default": ""  # Empty to avoid interference with OpenAI responses
            }
        }
    
    def get_user_profile(self, user_id: str) -> UserProfile:
        """Get or create user profile"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserProfile(
                user_id=user_id,
                communication_style="supportive",  # default
                preferred_pace="moderate",
                emotional_sensitivity="medium",
                learning_style="reading",
                session_history=[]
            )
        return self.user_profiles[user_id]
    
    def personalize_response(self, base_response: Dict[str, Any], 
                           emotional_tone: EmotionalTone, 
                           user_id: str) -> Dict[str, Any]:
        """Personalize coaching response based on user profile and emotional tone"""
        profile = self.get_user_profile(user_id)
        
        # Determine emotional state priority
        primary_emotion = self._get_primary_emotion(emotional_tone)
        
        # Select appropriate response template
        template_key = self._select_template_key(emotional_tone, primary_emotion)
        
        # Get personalized message
        personalized_message = self.response_templates[profile.communication_style].get(
            template_key, 
            self.response_templates[profile.communication_style]["default"]
        )
        
        # Modify base response
        personalized_response = {
            "personalized_message": personalized_message,
            "communication_style": profile.communication_style,
            "detected_emotion": primary_emotion,
            "adaptation_notes": self._generate_adaptation_notes(emotional_tone, profile)
        }
        
        return personalized_response
    
    def _get_primary_emotion(self, emotional_tone: EmotionalTone) -> str:
        """Identify the primary emotion from the analysis"""
        if not emotional_tone.emotions:
            return "neutral"
        
        # Find emotion with highest score
        primary_emotion = max(emotional_tone.emotions.items(), key=lambda x: x[1])
        
        # Only return if score is significant
        if primary_emotion[1] > 0.3:
            return primary_emotion[0]
        
        return "neutral"
    
    def _select_template_key(self, emotional_tone: EmotionalTone, primary_emotion: str) -> str:
        """Select appropriate template key based on emotional analysis"""
        # Map emotions to template keys
        emotion_mapping = {
            "anxiety": "high_anxiety",
            "frustration": "frustration",
            "confidence": "default",
            "sadness": "low_confidence",
            "excitement": "excitement",
            "confusion": "low_confidence",
            "hope": "default",
            "anger": "frustration"
        }
        
        # Handle low confidence based on overall sentiment
        if emotional_tone.sentiment == "negative" and emotional_tone.confidence > 0.5:
            return "low_confidence"
        
        return emotion_mapping.get(primary_emotion, "default")
    
    def _generate_adaptation_notes(self, emotional_tone: EmotionalTone, 
                                 profile: UserProfile) -> List[str]:
        """Generate notes about how the response was adapted"""
        notes = []
        
        if emotional_tone.sentiment == "negative":
            notes.append("Response adapted for negative emotional state")
        
        if emotional_tone.intensity > 0.7:
            notes.append("High emotional intensity detected - using gentler approach")
        
        if profile.emotional_sensitivity == "high":
            notes.append("Adjusted for high emotional sensitivity")
        
        return notes
    
    def update_user_profile(self, user_id: str, session_data: Dict[str, Any]):
        """Update user profile based on session data"""
        profile = self.get_user_profile(user_id)
        
        # Add session to history
        profile.session_history.append({
            "timestamp": session_data.get("timestamp"),
            "topic": session_data.get("topic"),
            "emotional_patterns": session_data.get("emotional_patterns", []),
            "preferred_interactions": session_data.get("preferred_interactions", [])
        })
        
        # Adapt communication style based on patterns
        if len(profile.session_history) >= 3:
            self._adapt_communication_style(profile)
    
    def _adapt_communication_style(self, profile: UserProfile):
        """Adapt communication style based on user patterns"""
        recent_sessions = profile.session_history[-3:]
        
        # Analyze patterns in recent sessions
        emotional_patterns = []
        for session in recent_sessions:
            emotional_patterns.extend(session.get("emotional_patterns", []))
        
        # Count emotional sensitivity indicators
        high_sensitivity_count = sum(1 for pattern in emotional_patterns 
                                   if pattern in ["anxiety", "overwhelm", "stress"])
        
        # Adjust sensitivity level
        if high_sensitivity_count >= 2:
            profile.emotional_sensitivity = "high"
            if profile.communication_style == "challenging":
                profile.communication_style = "supportive"
        
        # Store updated profile (in production, save to database)
        self.user_profiles[profile.user_id] = profile 