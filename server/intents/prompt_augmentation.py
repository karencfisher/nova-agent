from transformers import pipeline
import json
from collections import defaultdict


class PromptAugmentation:
    emotion_2_affect = {
        "admiration": "upbeat", "amusement": "upbeat", "anger": "direct",
        "annoyance": "direct", "approval": "upbeat", "caring": "supportive",
        "confusion": "reassuring", "curiosity": "exploratory", "desire": "exploratory",
        "disappointment": "supportive", "disapproval": "direct", "disgust": "direct",
        "embarrassment": "supportive", "excitement": "upbeat", "fear": "supportive",
        "gratitude": "upbeat", "grief": "supportive", "joy": "upbeat", "love": "upbeat",
        "nervousness": "supportive", "optimism": "upbeat", "pride": "upbeat",
        "realization": "reassuring", "relief": "upbeat", "remorse": "supportive",
        "sadness": "supportive", "surprise": "upbeat", "neutral": "neutral",
    }

    emotion_clf = pipeline(
        "text-classification",
        model="SamLowe/roberta-base-go_emotions",
        top_k=None
    )

    intent_clf = pipeline(
        "zero-shot-classification", 
        model="facebook/bart-large-mnli",
        top_k=1
    )
    labels = ['support', 'question', 'task', 'research', 'coding', 'meta', 'chitchat']

    @classmethod
    def get_affect(cls, text):
        emotions = cls.emotion_clf(text)[0]
        affect_scores = defaultdict(int)
        for emotion in emotions:
            affect_scores[cls.emotion_2_affect[emotion['label']]] += emotion['score']
        affect = max(affect_scores, key=affect_scores.get)
        score = affect_scores[affect]
        return {'label': affect, 'score': score}
    
    @classmethod
    def get_intent(cls, text):
        result = cls.intent_clf(text, cls.labels)
        intents = list(zip(result['scores'], result['labels']))
        intent = max(intents)
        return {'label': intent[1], 'score': intent[0]}

    @classmethod
    def make_structured_prompt(cls, text):
        prompt = {
            'text': text,
            'metadata': {
                'affect': cls.get_affect(text),
                'intent': cls.get_intent(text)
            }
        }
        return prompt

