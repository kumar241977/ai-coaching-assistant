# AI-Powered Virtual Coaching Assistant

A sophisticated virtual coaching assistant that provides structured coaching conversations aligned with ICF (International Coaching Federation) core competencies. The assistant offers personalized support across various professional development topics.

## 🎯 Features

### ICF-Aligned Coaching Framework
- **Establishing Trust and Intimacy**: Creates a safe, supportive environment
- **Active Listening**: Demonstrates deep understanding through reflection and clarification
- **Powerful Questioning**: Uses thought-provoking questions to deepen exploration
- **Creating Awareness**: Helps identify patterns, insights, and blind spots
- **Designing Actions**: Co-creates specific, actionable goals and plans
- **Managing Progress**: Tracks progress and maintains accountability

### Conversation Flow
1. **Intake**: Initial exploration of what the user wants to work on
2. **Exploration**: Deep dive into the chosen topic using active listening
3. **Reflection**: Creating awareness through insights and pattern recognition
4. **Action Planning**: Developing specific, committed actions
5. **Follow-up**: Progress tracking and accountability (future sessions)

### Personalization Engine
- **Emotional Tone Analysis**: Uses NLP to detect user's emotional state
- **Adaptive Responses**: Tailors coaching style based on user's needs
- **Communication Style Matching**: Adjusts between supportive, challenging, or direct approaches
- **Progress Tracking**: Maintains session history and user preferences

### Coaching Topics
- **Performance Improvement**: Enhancing work performance and productivity
- **Career Development**: Planning and advancing career growth
- **Work-Life Balance**: Achieving harmony between professional and personal life
- **Leadership Growth**: Developing leadership skills and effectiveness

## 🛠️ Technology Stack

- **Backend**: Python Flask
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Database**: SQLite (development), easily adaptable to PostgreSQL/MySQL
- **NLP Libraries**: 
  - TextBlob for sentiment analysis
  - VADER Sentiment for emotional tone detection
  - NLTK for text processing
- **UI Framework**: Custom responsive design with modern CSS

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-coaching-assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv coaching_env
   
   # Windows
   coaching_env\Scripts\activate
   
   # macOS/Linux
   source coaching_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download NLTK data** (first time only)
   ```python
   python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 🎮 Usage Guide

### Starting a Coaching Session

1. **Choose Your Focus**: Select from four coaching topics on the welcome screen
2. **Begin Conversation**: The assistant will guide you through structured exploration
3. **Engage Authentically**: Share your thoughts, challenges, and aspirations openly
4. **Follow the Flow**: Progress through Intake → Exploration → Reflection → Action Planning
5. **Commit to Action**: Create specific, measurable action commitments

### Example Session Flow

```
Coach: "Welcome! What would you like to work on today?"
User: "I'm struggling with work-life balance"

Coach: "Let's explore work-life balance. What areas of your life feel most out of balance right now?"
User: "I work late every night and barely see my family"

Coach: "I hear that work is consuming time you'd rather spend with family. What's driving those late work hours?"
User: "I feel like I can't keep up with everything during the day"

Coach: "What patterns do you notice in how you manage your daytime hours?"
User: "I get interrupted constantly and spend too much time in meetings"

Coach: "What would need to change for you to protect your evening time with family?"
User: "I need better boundaries and maybe more focused work time"

Coach: "What specific action could you take this week to create one protected evening?"
```

### API Endpoints

- `POST /api/start-session` - Initialize a new coaching session
- `POST /api/send-message` - Send message and receive coaching response
- `GET /api/session/<session_id>` - Retrieve session details
- `GET /api/sessions/<user_id>` - Get user's session history
- `POST /api/stage-transition` - Manually transition conversation stages

## 🏗️ Architecture Overview

```
ai-coaching-assistant/
├── app.py                    # Main Flask application
├── icf_competencies.py       # ICF coaching competency framework
├── conversation_flow.py      # Conversation stage management
├── nlp_personalization.py    # Emotional analysis and personalization
├── templates/
│   └── index.html           # Main UI template
├── static/
│   ├── styles.css           # Application styling
│   └── app.js              # Frontend JavaScript
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Core Components

1. **ICF Competency Framework** (`icf_competencies.py`)
   - Defines the six core ICF competencies
   - Provides response templates and follow-up questions
   - Maps competencies to conversation stages

2. **Conversation Flow Engine** (`conversation_flow.py`)
   - Manages conversation stages and transitions
   - Handles topic selection and progression
   - Maintains conversation state and history

3. **NLP Personalization Engine** (`nlp_personalization.py`)
   - Analyzes emotional tone using VADER and TextBlob
   - Adapts responses based on user's emotional state
   - Maintains user profiles and preferences

4. **Web Interface** (`templates/index.html`, `static/`)
   - Modern, responsive UI with smooth transitions
   - Real-time conversation flow
   - Visual progress indicators

## 🎨 Customization

### Adding New Coaching Topics

1. **Update conversation_flow.py**:
   ```python
   "new_topic": CoachingTopic(
       name="New Topic Name",
       description="Topic description",
       initial_questions=["Question 1", "Question 2"],
       exploration_areas=["area1", "area2"]
   )
   ```

2. **Update the UI** in `templates/index.html`:
   ```html
   <div class="topic-card" data-topic="new_topic">
       <i class="fas fa-icon-name"></i>
       <h4>New Topic Name</h4>
       <p>Topic description</p>
   </div>
   ```

### Customizing Response Styles

Modify the response templates in `nlp_personalization.py`:

```python
"supportive": {
    "high_anxiety": "Custom supportive response for anxiety",
    "frustration": "Custom supportive response for frustration",
    # ... more templates
}
```

### Adding New ICF Competencies

Extend the `ICFCompetency` enum and add corresponding responses in `icf_competencies.py`.

## 🔧 Development

### Running in Development Mode
```bash
export FLASK_ENV=development  # Linux/macOS
set FLASK_ENV=development     # Windows
python app.py
```

### Testing
```bash
# Run basic functionality tests
python -m pytest tests/

# Manual testing endpoints
curl -X POST http://localhost:5000/api/start-session \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test_user"}'
```

### Database Schema

The application uses SQLite with the following tables:

- **sessions**: Stores coaching session data
- **users**: Stores user preferences and profiles

## 🚀 Deployment

### Production Setup

1. **Use a production WSGI server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Environment Variables**:
   ```bash
   export SECRET_KEY="your-secret-key"
   export DATABASE_URL="your-database-url"
   ```

3. **Database Migration**: Replace SQLite with PostgreSQL for production

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **International Coaching Federation (ICF)** for the coaching competency framework
- **TextBlob & VADER** for sentiment analysis capabilities
- **Flask** community for the excellent web framework

## 🔮 Future Enhancements

- **AI Integration**: Connect with OpenAI GPT for more sophisticated responses
- **Voice Interface**: Add speech-to-text and text-to-speech capabilities
- **Mobile App**: Native iOS/Android applications
- **Analytics Dashboard**: Detailed insights and progress tracking
- **Multi-language Support**: Internationalization and localization
- **Integration APIs**: Connect with calendar, CRM, and productivity tools

## 📞 Support

For questions, issues, or contributions, please:
- Open an issue on GitHub
- Contact the development team
- Join our community discussions

---

**Built with ❤️ for coaches and coachees everywhere** 