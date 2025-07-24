from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

class ICFCompetency(Enum):
    ESTABLISHING_TRUST = "establishing_trust_and_intimacy"
    ACTIVE_LISTENING = "active_listening"
    POWERFUL_QUESTIONING = "powerful_questioning"
    CREATING_AWARENESS = "creating_awareness"
    DESIGNING_ACTIONS = "designing_actions"
    MANAGING_PROGRESS = "managing_progress_and_accountability"

@dataclass
class CompetencyResponse:
    competency: ICFCompetency
    response_template: str
    follow_up_questions: List[str]
    indicators: List[str]

class ICFCompetencyFramework:
    def __init__(self):
        self.competencies = self._initialize_competencies()
    
    def _initialize_competencies(self) -> Dict[ICFCompetency, CompetencyResponse]:
        return {
            ICFCompetency.ESTABLISHING_TRUST: CompetencyResponse(
                competency=ICFCompetency.ESTABLISHING_TRUST,
                response_template="I appreciate you sharing this with me. This feels like a safe space where we can explore this together.",
                follow_up_questions=[
                    "What feels most important to you about this situation?",
                    "How comfortable do you feel discussing this openly?",
                    "What would make this conversation most valuable for you?"
                ],
                indicators=["trust", "safety", "openness", "vulnerability"]
            ),
            
            ICFCompetency.ACTIVE_LISTENING: CompetencyResponse(
                competency=ICFCompetency.ACTIVE_LISTENING,
                response_template="What I'm hearing is... Is that accurate?",
                follow_up_questions=[
                    "Can you tell me more about that?",
                    "What else is important here?",
                    "Help me understand what you mean by..."
                ],
                indicators=["clarification", "paraphrasing", "reflection", "deeper_understanding"]
            ),
            
            ICFCompetency.POWERFUL_QUESTIONING: CompetencyResponse(
                competency=ICFCompetency.POWERFUL_QUESTIONING,
                response_template="I'm curious about...",
                follow_up_questions=[
                    "What would happen if...?",
                    "How does this connect to your broader goals?",
                    "What assumptions might you be making here?",
                    "What would success look like?",
                    "What's the real challenge behind this challenge?"
                ],
                indicators=["curiosity", "assumptions", "possibilities", "different_perspectives"]
            ),
            
            ICFCompetency.CREATING_AWARENESS: CompetencyResponse(
                competency=ICFCompetency.CREATING_AWARENESS,
                response_template="I notice... What do you make of that?",
                follow_up_questions=[
                    "What patterns do you see here?",
                    "What's working well that you might build on?",
                    "What blind spots might exist?",
                    "How does this align with your values?"
                ],
                indicators=["patterns", "insights", "blind_spots", "values_alignment"]
            ),
            
            ICFCompetency.DESIGNING_ACTIONS: CompetencyResponse(
                competency=ICFCompetency.DESIGNING_ACTIONS,
                response_template="Based on what we've explored, what feels like the right next step?",
                follow_up_questions=[
                    "What specific action will you take?",
                    "By when will you do this?",
                    "What support do you need?",
                    "How will you know you've succeeded?",
                    "What might get in the way?"
                ],
                indicators=["specific_actions", "timeline", "commitment", "obstacles"]
            ),
            
            ICFCompetency.MANAGING_PROGRESS: CompetencyResponse(
                competency=ICFCompetency.MANAGING_PROGRESS,
                response_template="Let's check in on your progress since our last conversation.",
                follow_up_questions=[
                    "What progress have you made?",
                    "What worked well?",
                    "What challenges did you encounter?",
                    "What adjustments do we need to make?",
                    "What have you learned about yourself?"
                ],
                indicators=["progress_review", "adjustments", "learning", "accountability"]
            )
        }
    
    def get_competency_response(self, competency: ICFCompetency) -> CompetencyResponse:
        return self.competencies[competency]
    
    def suggest_next_competency(self, current_stage: str, conversation_context: Dict) -> ICFCompetency:
        """Suggest the next ICF competency to apply based on conversation stage and context"""
        stage_mapping = {
            "intake": ICFCompetency.ESTABLISHING_TRUST,
            "exploration": ICFCompetency.ACTIVE_LISTENING,
            "deepening": ICFCompetency.POWERFUL_QUESTIONING,
            "reflection": ICFCompetency.CREATING_AWARENESS,
            "action_planning": ICFCompetency.DESIGNING_ACTIONS,
            "follow_up": ICFCompetency.MANAGING_PROGRESS
        }
        return stage_mapping.get(current_stage, ICFCompetency.ACTIVE_LISTENING) 