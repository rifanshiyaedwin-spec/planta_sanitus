# Minimal disease knowledge base

DISEASE_KNOWLEDGE_BASE = {
    'healthy': {
        'name': 'Healthy',
        'symptoms': 'Leaves show no visible disease signs.',
        'treatment': 'Maintain good agronomic practices.'
    },
    'early_blight': {
        'name': 'Early Blight',
        'symptoms': 'Small brown spots on leaves that expand.',
        'treatment': 'Remove affected leaves, apply appropriate fungicide.'
    },
    'late_blight': {
        'name': 'Late Blight',
        'symptoms': 'Dark lesions, rapid spread in wet conditions.',
        'treatment': 'Isolate plant, use certified fungicides, remove debris.'
    }
}

def get_disease_info(label_key):
    return DISEASE_KNOWLEDGE_BASE.get(label_key, {'name': label_key, 'symptoms':'N/A','treatment':'N/A'})
