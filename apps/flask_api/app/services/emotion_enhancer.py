import numpy as np
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


class EmotionEnhancer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

        self.stress_keywords = {
            'urgent': 1.0, 'immediately': 1.0, 'deadline': 0.9, 'pressure': 0.9,
            'stress': 1.0, 'critical': 1.0, 'emergency': 1.0, 'asap': 1.0,
            'rush': 0.8, 'overwhelm': 0.8, 'late': 0.7, 'missed': 0.8, '!': 0.9,
            'failure': 1.0, 'problem': 0.8, 'issue': 0.7, 'panic': 1.0,
            'struggle': 0.8, 'blocked': 0.8, 'escalate': 0.9, 'disaster': 1.0,
            'alarm': 0.8, 'extreme': 0.8, 'imense': 0.8, 'horible': 0.8,
            'tired': 0.6, 'right now': 0.9, 'dead': 0.8, 'fucked': 0.5, 'help': 0.8
        }

        self.relaxation_keywords = {
            'relax': 1.0, 'calm': 1.0, 'peaceful': 1.0, 'comfortable': 0.8,
            'easy': 0.8, 'smooth': 0.7, 'flexible': 0.7, 'convenient': 0.7,
            'happy': 0.7, 'pleasure': 0.7, 'thanks': 0.5, 'appreciate': 0.5,
            'good job': 0.9, 'well done': 0.9, 'casual': 0.6,
            'rest': 1.0, 'breathe': 1.0, 'enjoy': 0.8, 'serene': 1.0,
            'vacation': 1.0, 'holiday': 0.9, 'tranquil': 1.0
        }

        self.casual_indicators = [
            'lol', 'hey', 'yo', 'cool', 'bro', 'dude', 'kinda', 'wanna', 'gonna',
            'chill', 'brb', 'idk', 'omg', 'lmao', 'haha', 'sup', 'what’s up',
            'ttyl', 'gr8', 'meh', 'nah', 'btw', 'wha', 'ow', 'ngl', 'gl', 'gg',
            'jas', 'pls', 'ha', 'fuck'
        ]

        self.formal_indicators = [
            'dear', 'regards', 'sincerely', 'attached', 'please find', 'kindly',
            'respectfully', 'mr.', 'ms.', 'thank you', 'enclosed', 'appreciate',
            'to whom it may concern', 'yours faithfully', 'reference', 'request',
            'kind', 'regards'
        ]

        self.sarcasm_indicators = [
            'oh great', 'love that', 'awesome job', 'fantastic', 'just perfect',
            'can’t wait', 'what a surprise', 'sure thing', 'wonderful', 'amazing',
            'exactly what I needed', 'brilliant', 'how lovely', 'yay', 'genius'
        ]

    def detect_keywords(self, text, keyword_dict):
        score = 0.0
        for word, weight in keyword_dict.items():
            pattern = re.escape(word)
            matches = re.findall(pattern, text)
            score += len(matches) * weight
        return min(score / 5.0, 1.0)

    def handle_negation(self, text, score):
        negations = ['not', 'never', 'no']
        for neg in negations:
            if re.search(rf'\b{neg}\b.*\b(urgent|stress|critical|pressure)\b', text):
                return score * 0.3
        return score

    def detect_tone_scores(self, text):
        text_lower = text.lower()

        casual_score = 0
        formal_score = 0
        sarcasm_score = 0

        # CASUAL patterns
        casual_patterns = [
            r"\b(hey+|yo+|sup|lol+|lmao|rofl|idk|bruh+|nah|yup|nope|gonna|wanna|btw|jk|brb|tbh|irl|bff|omg|smh|wtf|wth|fyi|hbu|afaik|asap|rn|tho|fr|cya|ily|np|omfg|ikr|yolo|nvm|gg|tysm|atm|btw|pls|thx|gr8)\b",
            r"\b(relax|whatever|no big deal|i guess|all good|i mean|lowkey|highkey|kinda|sorta|sounds good|cool with that|not really|meh|same here|not bad|feels nice|easy stuff|so easy|nothing crazy|vibin|just chillin|doing nothing|kinda tired|bored af|need a break|feelin lazy|just saying|just sayin|anyways|stuff like that)\b",
            r"\b(dude|bro+|sis|man|fam|bestie|babe|homie|buddy|pal|mate|gang|my guy|my girl|queen|king|legend|goat|partner|bruv|gurl)\b",
            r"[🤙😂😅😎👍💀✨🔥💯🥴😭❤️‍🔥🤡🙃🤷‍♂️🤷‍♀️🤣😩🥲🫠🫶🏽🤞👀👊👏👐😬😉😊😍😘😜😝🤪🫡🆒]",
            r"[!?]{2,}",
            r"\b(let's hang|grab a drink|get lit|hit me up|pull up|come thru|just chillin|doing nothing|nothing much|wanna chill|down to go|goin out|need a break|out n about|bored af|taking it easy|catch up|party time|on my way|rolling through|link up|kick it|hang around|hang out|see you there)\b",
            r"\b(like|you know|literally|basically|honestly|actually|so yeah|not gonna lie|ngl|deadass|no cap|for real|low effort|idc|IDC|lmk|LMK|tbh|vibes|vibe check|eh|chillin|lazy day|funny af|crazy lol)\b",
        ]

        formal_patterns = [
            r"\b(dear|regards|best regards|kind regards|warm regards|sincerely|respectfully|to whom it may concern|yours faithfully|yours sincerely|with appreciation|with respect|cordially)\b",
            r"\b(please|kindly|we kindly request|i would appreciate|we would appreciate|we respectfully ask|i humbly request|it would be appreciated|would you be so kind|your attention is requested|your cooperation is appreciated|should you have any questions|we thank you for your time|please be advised that|we would like to inform you|i hope this message finds you well)\b",
            r"\b(mr\.|ms\.|mrs\.|dr\.|prof\.|ceo|cto|cfo|director|coordinator|manager|supervisor|executive|president|chairperson|administrator|head of department|team lead)\b",
            r"\b(i am writing to|this is to inform you that|in accordance with|as per our agreement|as previously discussed|as mentioned earlier|in light of|pursuant to|in response to|with reference to|as stated above|effective immediately|in the meantime|at your earliest convenience|in compliance with|with regard to|attached herewith|please find attached|enclosed you will find|we hereby|this serves as|we remain at your disposal)\b",
            r"\b(hereby|therefore|nevertheless|notwithstanding|therein|herein|forthwith|hereafter|aforementioned|henceforth|shall be|must comply|regarding|whereas|hence|forthcoming|obliged to|obligated to)\b",
            r"\b(official request|memorandum|agenda|minutes|schedule|reminder|internal memo|proposal|approval needed|documentation|feedback form|action item|performance review|onboarding process|training material|compliance report|assessment|citation|references|summary report|executive summary|evaluation form|submitted by|to be reviewed|enclosed)\b",
            r"\b(abstract|methodology|literature review|empirical|qualitative|quantitative|peer-reviewed|submission deadline|supervised by|affiliated with|dissertation|research paper|academic advisor|university policy|plagiarism check|committee meeting|grant proposal|conference proceedings|publication request)\b",
            r"[.,;:]",
        ]

        sarcasm_patterns = [
            r"\b(oh great|wonderful|amazing|just perfect|awesome|love that|fantastic job|brilliant move|how nice)\b",
            r"\b(yeah right|can’t wait|thanks a lot|sure thing|nice work|lovely|couldn’t be better|exactly what i wanted)\b",
            r"\b(not like i care|what could go wrong|i’m so thrilled|that’s just what i needed|classic|as always)\b",
            r"\b(thanks for nothing|as expected|again with this|surprise surprise|unbelievable)\b",
            r"\b(and they say miracles don’t happen|absolutely flawless|just in time as usual)\b",
            r"(!{2,}|\?{2,})",
            r"[🙃😒😑🤡👏👏👏😬😤🙄🫠💀]"
        ]

        def apply_patterns(patterns):
            return sum(bool(re.search(p, text_lower)) for p in patterns)

        casual_score += apply_patterns(casual_patterns)
        formal_score += apply_patterns(formal_patterns)
        sarcasm_score += apply_patterns(sarcasm_patterns)

        casual_score += text_lower.count("lol") + text_lower.count("😂")
        formal_score += sum(text_lower.count(w) for w in ["please", "kindly", "attached", "sincerely", "regards"])
        sarcasm_score += text_lower.count("oh great") + text_lower.count("thanks a lot")

        scores = {
            "casual": casual_score,
            "formal": formal_score,
            "sarcasm": sarcasm_score
        }

        total = sum(scores.values())

        if total == 0:
            return {
                "tone": "unknown",
                "casual_score": 0,
                 "formal_score": 0,
                "sarcasm_score": 0
            }
        else:
            percentages = {k: round(v / total * 100) for k, v in scores.items()}
            tone = max(percentages, key=percentages.get)
            if percentages[tone] < 35:
                tone = "unknown"
            return {
                "tone": tone,
                "casual_score": percentages["casual"],
                "formal_score": percentages["formal"],
                "sarcasm_score": percentages["sarcasm"]
        }

    def enhance_emotion_analysis(self, text):
        if isinstance(text, float) and np.isnan(text):
            return {
                "polarity": 0,
                "subjectivity": 0,
                "stress_score": 0,
                "relaxation_score": 0,
                "casual_score": 0,
                "formal_score": 0,
                "sarcasm_score": 0
            }

        text = str(text).lower()

        sentiment = self.analyzer.polarity_scores(text)
        polarity = sentiment["compound"]
        subjectivity = 0.5  # placeholder

        stress_score = self.detect_keywords(text, self.stress_keywords)
        relaxation_score = self.detect_keywords(text, self.relaxation_keywords)

        stress_score = self.handle_negation(text, stress_score)
        relaxation_score = self.handle_negation(text, relaxation_score)

        tone_scores = self.detect_tone_scores(text)

        casual_score = tone_scores["casual_score"]
        formal_score = tone_scores["formal_score"]
        sarcasm_score = tone_scores["sarcasm_score"]


        return {
            "polarity": polarity,
            "subjectivity": subjectivity,
            "stress_score": stress_score,
            "relaxation_score": relaxation_score,
            "casual_score": casual_score,
            "formal_score": formal_score,
            "sarcasm_score": sarcasm_score
        }

