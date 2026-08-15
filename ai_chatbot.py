import os
import random

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Simple rule-based agribot

def ask_agribot(query, lang='en'):
    q = (query or '').lower()
    if not q:
        return {'answer': 'Please ask a question about crops, pests, soil, or marketplace.'}

    if 'watering' in q or 'water' in q:
        return {'answer': 'Water young plants early in the morning. Avoid overwatering to prevent root rot.'}
    if 'fertil' in q or 'nitrogen' in q or 'npk' in q:
        return {'answer': 'Apply balanced NPK as per soil test. Use organic compost when possible.'}
    if 'disease' in q or 'blight' in q or 'pest' in q:
        return {'answer': 'Upload leaf images using the Diagnose tool; it will provide likely causes and treatment steps.'}

    # Default fallback
    generic = [
        'Could you provide more details about the crop and symptoms?',
        'I recommend running a soil test and uploading leaf images for an accurate diagnosis.'
    ]
    return {'answer': random.choice(generic)}
