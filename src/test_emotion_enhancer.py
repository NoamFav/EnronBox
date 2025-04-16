import unittest
from emotion_enhancer import EmotionEnhancer


class TestEmotionEnhancer(unittest.TestCase):
    def setUp(self):
        self.enhancer = EmotionEnhancer()

    def print_result(self, text, result):
        print(f"---\nInput: {text}")
        print(f"Polarity: {result['polarity']}")
        print(f"Subjectivity: {result['subjectivity']}")
        print(f"Stress Score: {result['stress_score']}")
        print(f"Relaxation Score: {result['relaxation_score']}")
        print(
            f"Tone Scores: [casual: {result['casual_score']}%, "
            f"formal: {result['formal_score']}%, "
            f"sarcasm: {result['sarcasm_score']}%]"
        )
        print(f"Dominant Tone: {self.get_dominant_tone(result)}\n---")

    def get_dominant_tone(self, result):
        tone_scores = {
            "casual": result.get("casual_score", 0),
            "formal": result.get("formal_score", 0),
            "sarcasm": result.get("sarcasm_score", 0),
        }
        max_tone = max(tone_scores, key=tone_scores.get)
        return max_tone if tone_scores[max_tone] >= 35 else "unknown"

    def assert_dominant_tone(self, result, expected):
        detected = self.get_dominant_tone(result)
        self.assertEqual(detected, expected)

    def test_neutral_message(self):
        text = "Let's schedule a meeting for next week."
        result = self.enhancer.enhance_emotion_analysis(text)
        self.print_result(text, result)
        self.assert_dominant_tone(result, "formal")

    def test_stress_message(self):
        text = "We are under extreme pressure to meet the deadline immediately. It's critical!"
        result = self.enhancer.enhance_emotion_analysis(text)
        self.print_result(text, result)
        self.assertGreater(result["stress_score"], 0.5)
        self.assert_dominant_tone(result, "formal")

    def test_relaxation_message(self):
        text = "Everything is going smoothly. Just relax and enjoy the process."
        result = self.enhancer.enhance_emotion_analysis(text)
        self.print_result(text, result)
        self.assertGreaterEqual(result["relaxation_score"], 0.4)

    def test_casual_message(self):
        text = "Hey dude, lol that was kinda cool. Wanna grab a drink?"
        result = self.enhancer.enhance_emotion_analysis(text)
        self.print_result(text, result)
        self.assert_dominant_tone(result, "casual")

    def test_formal_message(self):
        text = "Dear team, please find attached the revised report. Kindly review at your earliest convenience."
        result = self.enhancer.enhance_emotion_analysis(text)
        self.print_result(text, result)
        self.assert_dominant_tone(result, "formal")

    def test_sarcastic_message(self):
        text = "Oh great, another amazing update that breaks everything. Love that!"
        result = self.enhancer.enhance_emotion_analysis(text)
        self.print_result(text, result)
        self.assert_dominant_tone(result, "sarcasm")

    def test_long_formal_content(self):
        text = (
            "The Oxford Princeton Programme\n"
            "~~~~~~~~~~~~~~~~~~~~~~~~\n"
            "The world's leading provider of complete training solutions\n"
            "for the energy industry and beyond..."
        )
        result = self.enhancer.enhance_emotion_analysis(text)
        self.print_result(text, result)
        self.assert_dominant_tone(result, "formal")


if __name__ == '__main__':
    unittest.main()
