# Running AI Coaching Assistant on Replit

Since you don't have admin access to install Python locally, you can run the coaching assistant online using Replit.

## Step-by-Step Setup on Replit

### 1. Create Replit Account
- Go to https://replit.com
- Sign up for a free account
- Click "Create Repl"

### 2. Create New Flask Project
- Choose "Python" or "Flask" template
- Name your project "ai-coaching-assistant"
- Click "Create Repl"

### 3. Upload Your Files
Upload all these files to your Replit project:
- `app.py`
- `icf_competencies.py` 
- `conversation_flow.py`
- `nlp_personalization.py`
- `coaching_scenarios.py`
- `requirements.txt`
- `templates/index.html`
- `static/styles.css`
- `static/app.js`

### 4. Install Dependencies
In the Replit terminal, run:
```bash
pip install -r requirements.txt
```

### 5. Download NLTK Data
Run this in the Replit terminal:
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"
```

### 6. Run the Application
```bash
python app.py
```

The coaching assistant will be available at the URL Replit provides!

## Alternative: Trinket
If Replit doesn't work:
1. Go to https://trinket.io
2. Create a Python project
3. Upload your files
4. Run the application

## Alternative: Gitpod
1. Go to https://gitpod.io
2. Connect your GitHub account
3. Upload files to GitHub first
4. Open in Gitpod workspace

## Files You Need to Upload
Make sure you have all these files from your project:

```
ai-coaching-assistant/
├── app.py
├── icf_competencies.py
├── conversation_flow.py
├── nlp_personalization.py
├── coaching_scenarios.py
├── requirements.txt
├── templates/
│   └── index.html
├── static/
│   ├── styles.css
│   └── app.js
└── README.md
```

## Troubleshooting on Replit

### If you get import errors:
```bash
pip install flask flask-cors textblob vaderSentiment nltk
```

### If NLTK data is missing:
```python
import nltk
nltk.download('all')
```

### If the app doesn't start:
- Make sure `app.py` is in the root directory
- Check that all file paths are correct
- Ensure templates and static folders exist

## Running Locally with Portable Python

If you prefer to run locally, download WinPython:
1. Download from https://winpython.github.io/
2. Extract to your Documents folder
3. Use the WinPython Command Prompt
4. Navigate to your project folder
5. Run: `python app.py`

Your AI coaching assistant will be ready to use! 