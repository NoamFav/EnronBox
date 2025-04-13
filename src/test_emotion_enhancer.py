import unittest
from emotion_enhancer import EmotionEnhancer

class TestEmotionEnhancer(unittest.TestCase):

    def setUp(self):
        self.enhancer = EmotionEnhancer()

    def test_neutral_text(self):
        text = "This is a regular email about scheduling a meeting."
        result = self.enhancer.enhance_emotion_analysis(text)
        print("\n[Neutral] Result:", result)
        self.assertAlmostEqual(result["polarity"], 0.0, delta=0.2)
        self.assertEqual(result["stress_score"], 0.0)
        self.assertEqual(result["relaxation_score"], 0.0)

    def test_stressful_text(self):
        text = "URGENT: We have a critical deadline and the issue must be fixed immediately!"
        result = self.enhancer.enhance_emotion_analysis(text)
        print("\n[Stressful] Result:", result)
        self.assertLess(result["polarity"], 0)
        self.assertGreater(result["stress_score"], 0)
        self.assertEqual(result["relaxation_score"], 0)

    def test_relaxing_text(self):
        text = "Thanks for the great work! It's a pleasure working in such a calm and flexible environment."
        result = self.enhancer.enhance_emotion_analysis(text)
        print("\n[Relaxing] Result:", result)
        self.assertGreater(result["polarity"], 0)
        self.assertEqual(result["stress_score"], 0)
        self.assertGreater(result["relaxation_score"], 0)

    def test_mixed_emotions(self):
        text = "I appreciate your help, but I'm overwhelmed by the missed deadlines and ongoing problems."
        result = self.enhancer.enhance_emotion_analysis(text)
        print("\n[Mixed] Result:", result)
        self.assertLess(result["polarity"], 0)
        self.assertGreater(result["stress_score"], 0)
        self.assertGreater(result["relaxation_score"], 0)

    def test_nan_input(self):
        import numpy as np
        result = self.enhancer.enhance_emotion_analysis(np.nan)
        print("\n[Nan Input] Result:", result)
        self.assertEqual(result["polarity"], 0)
        self.assertEqual(result["subjectivity"], 0)
        self.assertEqual(result["stress_score"], 0)
        self.assertEqual(result["relaxation_score"], 0)

if __name__ == '__main__':
    unittest.main()
