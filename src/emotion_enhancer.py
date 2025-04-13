"""
emotion_enhancer.py - Adds stress/relaxation detection to email analysis
"""

import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class EmotionEnhancer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        # Stress indicators
        self.stress_keywords = [
            'urgent', 'immediately', 'deadline', 'pressure', 'stress',
            'critical', 'emergency', 'asap', 'rush', 'overwhelm',
            'late', 'missed', 'failure', 'problem', 'issue'
        ]

        # Relaxation indicators
        self.relaxation_keywords = [
            'relax', 'calm', 'peaceful', 'comfortable', 'easy',
            'smooth', 'flexible', 'convenient', 'happy', 'pleasure',
            'thanks', 'appreciate', 'good job', 'well done', 'casual'
        ]

    def enhance_emotion_analysis(self, text):
        """
        Extended emotion analysis using VADER + stress/relaxation keywords
        Returns:
        - polarity (compound score)
        - subjectivity (not provided by VADER, set to 0.5 placeholder)
        - stress_score
        - relaxation_score
        """
        if isinstance(text, float) and np.isnan(text):
            return {
                "polarity": 0,
                "subjectivity": 0,
                "stress_score": 0,
                "relaxation_score": 0
            }

        text = str(text).lower()

        # VADER sentiment analysis
        sentiment = self.analyzer.polarity_scores(text)
        polarity = sentiment["compound"]
        subjectivity = 0.5  # VADER doesn't provide this, you could remove it if unused

        # Stress detection
        stress_count = sum(text.count(word) for word in self.stress_keywords)
        stress_score = min(stress_count / 5, 1.0)

        # Relaxation detection
        relaxation_count = sum(text.count(word) for word in self.relaxation_keywords)
        relaxation_score = min(relaxation_count / 5, 1.0)

        return {
            "polarity": polarity,
            "subjectivity": subjectivity,
            "stress_score": stress_score,
            "relaxation_score": relaxation_score
        }