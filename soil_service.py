
def analyze_soil_health(ph, n, p, k, acres=1.0):
    # Simple NPK evaluation and advice
    score = 0
    advice = []
    # pH guidance
    if ph < 5.5:
        advice.append('Soil is acidic. Consider liming.')
    elif ph > 7.5:
        advice.append('Soil is alkaline. Consider sulfur or acidifying amendments.')
    else:
        advice.append('Soil pH is within optimal range.')

    # Nitrogen
    if n < 100:
        advice.append('Nitrogen is low. Apply nitrogen-rich fertilizer or compost.')
    elif n > 300:
        advice.append('Nitrogen is high. Reduce N fertilizer to avoid leaching.')
    else:
        advice.append('Nitrogen is adequate.')

    # Phosphorus
    if p < 20:
        advice.append('Phosphorus is low. Use phosphate fertilizers or bone meal.')
    else:
        advice.append('Phosphorus levels are sufficient.')

    # Potassium
    if k < 100:
        advice.append('Potassium is low. Apply potash or wood ash in small amounts.')
    else:
        advice.append('Potassium is adequate.')

    # Simple recommendation for amounts (very approximate)
    recommended_N = max(0, 150 - n)
    recommended_P = max(0, 40 - p)
    recommended_K = max(0, 150 - k)

    return {
        'ph': ph,
        'n': n,
        'p': p,
        'k': k,
        'acres': acres,
        'recommendations': advice,
        'recommended_addition_per_acre': {
            'N_kg': recommended_N,
            'P_kg': recommended_P,
            'K_kg': recommended_K
        }
    }
