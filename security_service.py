import html
import re

def sanitize_user_input(value):
    if value is None:
        return ''
    s = str(value).strip()
    # Minimal escape
    s = html.escape(s)
    # Remove control chars
    s = re.sub(r'[\x00-\x1f\x7f]', '', s)
    return s

def check_cia_security_status():
    # Return a mock compliance status
    return {
        'confidentiality': {'status': 'Good', 'notes': 'Passwords hashed; consider env secrets.'},
        'integrity': {'status': 'Good', 'notes': 'Database uses transactions.'},
        'availability': {'status': 'Moderate', 'notes': 'No cluster; single-instance availability.'}
    }
