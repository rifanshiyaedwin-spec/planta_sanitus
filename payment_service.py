import re
import random
import uuid

# Luhn algorithm for card validation

def luhn_check(card_number):
    try:
        digits = [int(d) for d in re.sub(r'\D', '', card_number)]
    except Exception:
        return False
    s = 0
    alt = False
    for d in reversed(digits):
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        s += d
        alt = not alt
    return s % 10 == 0

UPI_RE = re.compile(r'^[\w.-]{2,}@[\w]{2,}$')

def process_secure_payment(method, details, amount):
    method = (method or '').lower()
    if method == 'upi':
        upi = details.get('upi_id','')
        if not UPI_RE.match(upi):
            return {'success': False, 'error_message': 'Invalid UPI ID format.'}
        masked = upi[:3] + '***@' + upi.split('@')[-1]
    else:
        card = details.get('card_number','')
        if not luhn_check(card):
            return {'success': False, 'error_message': 'Invalid card number (Luhn failed).'}
        masked = '**** **** **** ' + card[-4:]

    # Simulate tokenization and txn
    token = uuid.uuid4().hex
    txn_id = 'TXN' + uuid.uuid4().hex[:10]
    return {'success': True, 'masked_account': masked, 'token': token, 'txn_id': txn_id}
