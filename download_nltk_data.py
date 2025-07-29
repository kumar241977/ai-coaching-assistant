#!/usr/bin/env python3
"""
Download required NLTK data for the coaching app
"""
import nltk
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

def download_nltk_data():
    """Download required NLTK data packages"""
    try:
        print("📥 Downloading NLTK data...")
        nltk.download('punkt', quiet=True)
        nltk.download('vader_lexicon', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("✅ NLTK data downloaded successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Could not download NLTK data: {e}")
        print("The app will still work, but some NLP features may be limited.")

if __name__ == "__main__":
    download_nltk_data() 