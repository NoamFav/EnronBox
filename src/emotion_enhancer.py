"""
emotion_enhancer.py - Adds stress/relaxation detection to email analysis
"""

import numpy as np
from textblob import TextBlob

class EmotionEnhancer:
    def __init__(self):
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
        Extended emotion analysis adding stress and relaxation detection
        Returns dict with:
        - polarity (existing)
        - subjectivity (existing)
        - stress_score (new)
        - relaxation_score (new)
        """
        if isinstance(text, float) and np.isnan(text):
            return {
                "polarity": 0,
                "subjectivity": 0,
                "stress_score": 0,
                "relaxation_score": 0
            }

        text = str(text).lower()

        # Existing TextBlob analysis
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        subjectivity = blob.sentiment.subjectivity

        # Stress detection
        stress_count = sum(text.count(word) for word in self.stress_keywords)
        stress_score = min(stress_count / 5, 1.0)  # Normalized to 0-1 range

        # Relaxation detection
        relaxation_count = sum(text.count(word) for word in self.relaxation_keywords)
        relaxation_score = min(relaxation_count / 5, 1.0)  # Normalized to 0-1 range

        return {
            "polarity": polarity,
            "subjectivity": subjectivity,
            "stress_score": stress_score,
            "relaxation_score": relaxation_score
        }
