# PlantaSanitus (planta_sanitus)

This repository contains a Flask-based smart agriculture platform demo. The implementation includes:

- app.py: Main Flask application (already added).
- Lightweight SQLite-backed database (database.py).
- Image-based heuristic predictor (predict.py).
- Weather, soil, QR, chatbot, payment, and security helper modules.

To run locally:

1. python -m venv venv
2. source venv/bin/activate  # or venv\Scripts\activate on Windows
3. pip install -r requirements.txt
4. export FLASK_APP=app.py
5. flask run

The app will create planta_sanitus.db in the project root and static/uploads at runtime.
