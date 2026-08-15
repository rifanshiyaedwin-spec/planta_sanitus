from PIL import Image
import os
import random

# Lightweight heuristic predictor using green channel analysis

def predict_multi_leaf_disease(image_paths):
    # Simple heuristic: measure green intensity to decide disease
    avg_green = 0.0
    samples = 0
    for p in image_paths:
        try:
            img = Image.open(p).convert('RGB').resize((200,200))
            pixels = list(img.getdata())
            g = sum(px[1] for px in pixels) / len(pixels)
            avg_green += g
            samples += 1
        except Exception:
            continue
    if samples:
        avg_green /= samples

    # Map to pseudo diseases
    if avg_green > 120:
        disease = 'Healthy'
        label = 'healthy'
        confidence = round(0.85 + random.random()*0.14, 2)
        severity = 0
        status = 'Good'
    elif avg_green > 90:
        disease = 'Early Blight'
        label = 'early_blight'
        confidence = round(0.7 + random.random()*0.25,2)
        severity = 30
        status = 'Moderate'
    else:
        disease = 'Late Blight'
        label = 'late_blight'
        confidence = round(0.65 + random.random()*0.3,2)
        severity = 70
        status = 'Severe'

    severity_level = 'Low' if severity < 30 else ('Medium' if severity < 60 else 'High')
    severity_percent = severity
    urgency = 'Low' if severity < 30 else ('Medium' if severity < 60 else 'High')
    recovery_time = '1-2 weeks' if severity < 30 else ('2-4 weeks' if severity < 60 else '4+ weeks')

    # XAI highlights: return bounding boxes as placeholders
    xai_highlights = []
    for i,p in enumerate(image_paths):
        xai_highlights.append({'image': os.path.basename(p), 'boxes': [{'x':10,'y':10,'w':50,'h':50}]})

    result = {
        'crop': 'Generic Crop',
        'disease': disease,
        'label_key': label,
        'status': status,
        'confidence': confidence,
        'severity_level': severity_level,
        'severity_percent': severity_percent,
        'urgency': urgency,
        'recovery_time': recovery_time,
        'scientific_name': 'N/A',
        'xai_highlights': xai_highlights
    }
    return result
