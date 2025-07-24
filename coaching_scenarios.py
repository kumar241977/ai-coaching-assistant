"""
Example Coaching Scenarios

This file contains example coaching conversations demonstrating how the AI coaching assistant
applies ICF competencies across different topics and stages.
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class ScenarioMessage:
    role: str  # 'coach' or 'user'
    content: str
    stage: str  # conversation stage
    competency: str  # ICF competency applied
    insights: List[str] = None

@dataclass
class CoachingScenario:
    title: str
    topic: str
    description: str
    user_profile: Dict[str, Any]
    conversation: List[ScenarioMessage]
    learning_objectives: List[str]

# Performance Improvement Scenario
performance_scenario = CoachingScenario(
    title="Overcoming Procrastination and Improving Productivity",
    topic="performance_improvement",
    description="A mid-level manager struggling with procrastination and feeling overwhelmed by their workload",
    user_profile={
        "role": "Marketing Manager",
        "experience": "5 years",
        "challenges": ["procrastination", "overwhelm", "time management"],
        "communication_style": "supportive"
    },
    conversation=[
        ScenarioMessage(
            role="coach",
            content="Welcome to your coaching session. I'm here to support you in exploring what's important to you. What would you like to work on today?",
            stage="intake",
            competency="establishing_trust_and_intimacy"
        ),
        ScenarioMessage(
            role="user",
            content="I've been struggling with getting things done at work. I keep putting off important tasks until the last minute, and it's causing me a lot of stress.",
            stage="intake",
            competency="establishing_trust_and_intimacy"
        ),
        ScenarioMessage(
            role="coach",
            content="Thank you for sharing that with me. I can hear that procrastination is creating stress for you. What I'm hearing is that this pattern of delaying important tasks is really impacting your well-being. Can you help me understand what's behind this pattern?",
            stage="exploration",
            competency="active_listening"
        ),
        ScenarioMessage(
            role="user",
            content="I think I'm just overwhelmed. I have so many projects and deadlines, and when I look at my to-do list, I just freeze. It feels impossible to know where to start.",
            stage="exploration",
            competency="active_listening"
        ),
        ScenarioMessage(
            role="coach",
            content="That feeling of being frozen when facing overwhelming tasks sounds really difficult. I'm curious - what would happen if you approached your to-do list differently? What assumptions might you be making about how you need to tackle everything?",
            stage="exploration",
            competency="powerful_questioning"
        ),
        ScenarioMessage(
            role="user",
            content="I guess I assume I need to do everything perfectly and all at once. Maybe I'm setting myself up to fail by thinking I have to complete entire projects in one sitting.",
            stage="exploration",
            competency="powerful_questioning"
        ),
        ScenarioMessage(
            role="coach",
            content="I notice you've identified a pattern here - the belief that you need to do everything perfectly and all at once. What do you make of that insight?",
            stage="reflection",
            competency="creating_awareness",
            insights=["Perfectionism is creating paralysis", "All-or-nothing thinking patterns", "Setting unrealistic expectations"]
        ),
        ScenarioMessage(
            role="user",
            content="It's like I'm creating this impossible standard for myself. No wonder I procrastinate - the task feels too big and scary to even start.",
            stage="reflection",
            competency="creating_awareness"
        ),
        ScenarioMessage(
            role="coach",
            content="Based on what we've explored and your insight about these impossible standards, what feels like the most important action you could take this week?",
            stage="action_planning",
            competency="designing_actions"
        ),
        ScenarioMessage(
            role="user",
            content="I want to try breaking down one big project into smaller, 15-minute tasks. Just to prove to myself that I can make progress without having to finish everything at once.",
            stage="action_planning",
            competency="designing_actions"
        )
    ],
    learning_objectives=[
        "Identify perfectionism as a root cause of procrastination",
        "Recognize all-or-nothing thinking patterns",
        "Develop strategies for breaking down overwhelming tasks",
        "Create manageable action steps for immediate implementation"
    ]
)

# Career Development Scenario
career_scenario = CoachingScenario(
    title="Navigating a Career Transition to Leadership",
    topic="career_development",
    description="A high-performing individual contributor considering a move to management",
    user_profile={
        "role": "Senior Software Developer",
        "experience": "8 years",
        "challenges": ["career transition", "leadership skills", "confidence"],
        "communication_style": "direct"
    },
    conversation=[
        ScenarioMessage(
            role="coach",
            content="I'm here to support you in your career exploration. What's bringing you to coaching today?",
            stage="intake",
            competency="establishing_trust_and_intimacy"
        ),
        ScenarioMessage(
            role="user",
            content="I've been offered a team lead position, but I'm not sure if I should take it. I'm good at coding, but managing people feels completely different.",
            stage="intake",
            competency="establishing_trust_and_intimacy"
        ),
        ScenarioMessage(
            role="coach",
            content="It sounds like you're at an important career crossroads. What excites you most about the potential leadership role?",
            stage="exploration",
            competency="powerful_questioning"
        ),
        ScenarioMessage(
            role="user",
            content="I like the idea of having more influence over the direction of projects and helping other developers grow. But I'm worried I'll be terrible at the people management part.",
            stage="exploration",
            competency="powerful_questioning"
        ),
        ScenarioMessage(
            role="coach",
            content="I hear both excitement about influence and impact, and some concern about people management. What evidence do you have about your ability to work with and support others?",
            stage="exploration",
            competency="powerful_questioning"
        ),
        ScenarioMessage(
            role="user",
            content="Well, I do mentor junior developers informally, and they seem to value my guidance. I've also led some cross-functional projects successfully.",
            stage="exploration",
            competency="powerful_questioning"
        ),
        ScenarioMessage(
            role="coach",
            content="I notice you're already demonstrating leadership skills - mentoring others and leading projects. Yet you're worried about being 'terrible' at people management. What's the gap between these two realities?",
            stage="reflection",
            competency="creating_awareness",
            insights=["Already demonstrating leadership skills", "Imposter syndrome around formal authority", "Gap between current abilities and self-perception"]
        ),
        ScenarioMessage(
            role="user",
            content="I think I'm underestimating what I already do well and overestimating what I don't know. Maybe the formal title is making it feel scarier than it is.",
            stage="reflection",
            competency="creating_awareness"
        ),
        ScenarioMessage(
            role="coach",
            content="What specific step could you take this week to test your leadership capabilities or address your concerns about people management?",
            stage="action_planning",
            competency="designing_actions"
        ),
        ScenarioMessage(
            role="user",
            content="I could have conversations with the current manager and a few team members to understand what the role really involves day-to-day. And maybe I could formally mentor one more junior developer to build my confidence.",
            stage="action_planning",
            competency="designing_actions"
        )
    ],
    learning_objectives=[
        "Recognize existing leadership capabilities",
        "Address imposter syndrome around formal leadership roles",
        "Develop strategies for transitioning from individual contributor to manager",
        "Create specific steps for informed decision-making"
    ]
)

# Work-Life Balance Scenario
work_life_scenario = CoachingScenario(
    title="Establishing Boundaries Between Work and Personal Life",
    topic="work_life_balance",
    description="A dedicated professional struggling to disconnect from work and maintain personal relationships",
    user_profile={
        "role": "Sales Director",
        "experience": "10 years",
        "challenges": ["boundaries", "personal relationships", "burnout"],
        "communication_style": "challenging"
    },
    conversation=[
        ScenarioMessage(
            role="coach",
            content="Welcome! What aspect of your life would you like to explore today?",
            stage="intake",
            competency="establishing_trust_and_intimacy"
        ),
        ScenarioMessage(
            role="user",
            content="My partner says I'm always working, even when I'm physically at home. I check emails during dinner, take calls on weekends. I know they're right, but I feel like I have to stay on top of everything.",
            stage="intake",
            competency="establishing_trust_and_intimacy"
        ),
        ScenarioMessage(
            role="coach",
            content="What would happen if you weren't available 24/7? What are you afraid might occur?",
            stage="exploration",
            competency="powerful_questioning"
        ),
        ScenarioMessage(
            role="user",
            content="I guess I'm afraid clients will go elsewhere if I'm not immediately responsive. My team might make mistakes without my input. I've built my reputation on being reliable and always available.",
            stage="exploration",
            competency="powerful_questioning"
        ),
        ScenarioMessage(
            role="coach",
            content="What evidence do you have that immediate availability is truly necessary for your success? Have you tested what happens when you're not instantly responsive?",
            stage="exploration",
            competency="powerful_questioning"
        ),
        ScenarioMessage(
            role="user",
            content="Actually, when I was sick last month and couldn't respond for a day, nothing catastrophic happened. My team handled things fine, and clients understood when I got back to them.",
            stage="exploration",
            competency="powerful_questioning"
        ),
        ScenarioMessage(
            role="coach",
            content="I'm noticing a pattern here. You believe constant availability is essential for success, yet when you tested it by being unavailable due to illness, everything functioned well. What does this tell you about your assumptions?",
            stage="reflection",
            competency="creating_awareness",
            insights=["Belief in necessity of constant availability may be unfounded", "Team and clients are more resilient than assumed", "Fear-based thinking driving overwork"]
        ),
        ScenarioMessage(
            role="user",
            content="Maybe I'm creating this pressure for myself unnecessarily. It's possible that my need to control everything is actually what's causing the problem, not solving it.",
            stage="reflection",
            competency="creating_awareness"
        ),
        ScenarioMessage(
            role="coach",
            content="What specific boundary could you establish this week to test whether you can maintain success while protecting your personal time?",
            stage="action_planning",
            competency="designing_actions"
        ),
        ScenarioMessage(
            role="user",
            content="I want to try not checking email after 7 PM on weekdays and staying offline completely on Sunday mornings. I'll set up an auto-responder explaining when people can expect to hear back from me.",
            stage="action_planning",
            competency="designing_actions"
        )
    ],
    learning_objectives=[
        "Challenge beliefs about necessity of constant availability",
        "Recognize control patterns that create overwork",
        "Test assumptions about client and team needs",
        "Establish specific, measurable boundaries"
    ]
)

# Leadership Growth Scenario
leadership_scenario = CoachingScenario(
    title="Developing Authentic Leadership Style",
    topic="leadership_growth",
    description="A new executive struggling to find their authentic leadership voice while managing a diverse team",
    user_profile={
        "role": "VP of Operations",
        "experience": "15 years",
        "challenges": ["authentic leadership", "team dynamics", "executive presence"],
        "communication_style": "supportive"
    },
    conversation=[
        ScenarioMessage(
            role="coach",
            content="I'm glad you're here. What leadership challenge would you like to explore today?",
            stage="intake",
            competency="establishing_trust_and_intimacy"
        ),
        ScenarioMessage(
            role="user",
            content="I was recently promoted to VP, and I feel like I'm trying to be someone I'm not. I keep switching between being too friendly and then too authoritative. I don't know what my leadership style should be.",
            stage="intake",
            competency="establishing_trust_and_intimacy"
        ),
        ScenarioMessage(
            role="coach",
            content="It sounds like you're experimenting with different approaches and haven't found what feels authentic yet. When you think about leaders you admire, what qualities do they possess?",
            stage="exploration",
            competency="active_listening"
        ),
        ScenarioMessage(
            role="user",
            content="The best leaders I've worked with were consistent. They were clear about expectations but also genuinely cared about people. They didn't pretend to have all the answers.",
            stage="exploration",
            competency="active_listening"
        ),
        ScenarioMessage(
            role="coach",
            content="Those are powerful qualities - consistency, clarity, genuine care, and humility. How do these align with who you naturally are as a person?",
            stage="exploration",
            competency="powerful_questioning"
        ),
        ScenarioMessage(
            role="user",
            content="Actually, those do sound like me. I've always been someone people come to for honest feedback and support. Maybe I'm overcomplicating this by trying to be some 'executive' version of myself.",
            stage="exploration",
            competency="powerful_questioning"
        ),
        ScenarioMessage(
            role="coach",
            content="I hear you recognizing that your natural qualities align with effective leadership. What's been driving you to create this 'executive version' rather than leading from your authentic self?",
            stage="reflection",
            competency="creating_awareness",
            insights=["Natural leadership qualities already present", "Trying to conform to external expectations", "Overcomplicating leadership by performing a role"]
        ),
        ScenarioMessage(
            role="user",
            content="I think I was worried that being myself wasn't 'executive enough.' Like I needed to be more formal or distant to be taken seriously at this level.",
            stage="reflection",
            competency="creating_awareness"
        ),
        ScenarioMessage(
            role="coach",
            content="Given this insight about your authentic leadership qualities, what's one way you could lead more authentically with your team this week?",
            stage="action_planning",
            competency="designing_actions"
        ),
        ScenarioMessage(
            role="user",
            content="I want to have one-on-ones with each team member where I'm genuinely curious about their challenges and goals, rather than just checking project status. I'll be myself - ask questions, listen, and be honest when I don't have answers.",
            stage="action_planning",
            competency="designing_actions"
        )
    ],
    learning_objectives=[
        "Identify authentic leadership qualities already possessed",
        "Challenge beliefs about 'executive' behavior expectations",
        "Recognize the power of leading from genuine self",
        "Create specific opportunities to practice authentic leadership"
    ]
)

# Collection of all scenarios
COACHING_SCENARIOS = {
    "performance_improvement": performance_scenario,
    "career_development": career_scenario,
    "work_life_balance": work_life_scenario,
    "leadership_growth": leadership_scenario
}

def get_scenario(topic: str) -> CoachingScenario:
    """Get a coaching scenario by topic"""
    return COACHING_SCENARIOS.get(topic)

def get_all_scenarios() -> Dict[str, CoachingScenario]:
    """Get all coaching scenarios"""
    return COACHING_SCENARIOS

def demonstrate_icf_competencies():
    """
    Demonstrate how ICF competencies are applied across different scenarios
    """
    competency_examples = {
        "establishing_trust_and_intimacy": [
            "Creating a safe, non-judgmental space",
            "Demonstrating genuine care and interest",
            "Being authentic and vulnerable when appropriate"
        ],
        "active_listening": [
            "Paraphrasing and reflecting back what was heard",
            "Asking clarifying questions",
            "Noticing what's not being said"
        ],
        "powerful_questioning": [
            "Asking open-ended questions that provoke insight",
            "Challenging assumptions gently",
            "Exploring different perspectives"
        ],
        "creating_awareness": [
            "Highlighting patterns and contradictions",
            "Reflecting insights back to the client",
            "Connecting dots between different parts of the conversation"
        ],
        "designing_actions": [
            "Co-creating specific, measurable actions",
            "Ensuring actions align with insights and goals",
            "Establishing accountability and timelines"
        ],
        "managing_progress": [
            "Following up on previous commitments",
            "Celebrating progress and learning",
            "Adjusting plans based on results"
        ]
    }
    
    return competency_examples

if __name__ == "__main__":
    # Example usage
    scenario = get_scenario("performance_improvement")
    print(f"Scenario: {scenario.title}")
    print(f"Description: {scenario.description}")
    print(f"Learning Objectives: {', '.join(scenario.learning_objectives)}")
    
    print("\nConversation Flow:")
    for i, message in enumerate(scenario.conversation[:5]):  # Show first 5 messages
        print(f"{i+1}. {message.role.upper()}: {message.content}")
        print(f"   [Stage: {message.stage}, Competency: {message.competency}]")
        print() 