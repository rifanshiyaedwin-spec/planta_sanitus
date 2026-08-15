"""
app.py - Master Application Server for PlantaSanitus Smart Agriculture Platform
Powers AI multi-image leaf diagnostics, XAI explainability, role-based auth (Farmer/Seller/Admin),
Soil Health NPK calculator, Weather Intelligence, Agro-Medicine E-Commerce Marketplace,
Order Tracking, CIA Triad Security Processor, Secured Payment Gateway, Seller Studio, and AgriBot AI Chatbot.
"""

import os
import time
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

import database as db
from predict import predict_multi_leaf_disease
from weather_service import get_weather_forecast
from soil_service import analyze_soil_health
from qr_service import generate_product_qr_code
from ai_chatbot import ask_agribot
from payment_service import process_secure_payment
from security_service import sanitize_user_input, check_cia_security_status
from disease_info import DISEASE_KNOWLEDGE_BASE, get_disease_info

app = Flask(__name__)
# Load secret from environment for production; fallback kept for local/dev convenience
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET', 'plantasanitus_enterprise_key_2026_secured')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # CIA Availability: 10MB upload limit

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
SAMPLES_FOLDER = os.path.join(app.root_path, 'static', 'samples')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(SAMPLES_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_user():
    user = None
    if 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
    return dict(current_user=user)

# --- AUTHENTICATION & ACCOUNT MANAGER ROUTES ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register account with Role selection (Farmer, Seller, Admin)."""
    if request.method == 'POST':
        username = sanitize_user_input(request.form.get('username', ''))
        email = sanitize_user_input(request.form.get('email', ''))
        password = request.form.get('password', '')
        role = sanitize_user_input(request.form.get('role', 'farmer'))
        full_name = sanitize_user_input(request.form.get('full_name', ''))
        phone = sanitize_user_input(request.form.get('phone', ''))

        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return redirect(url_for('register'))

        existing = db.get_user_by_username(username)
        if existing:
            flash('Username already exists. Please choose another.', 'error')
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)
        user_id = db.create_user(username, email, password_hash, role, full_name, phone)

        if user_id:
            session['user_id'] = user_id
            session['username'] = username
            session['role'] = role
            flash(f'Welcome to PlantaSanitus! Account created as {role.capitalize()}.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Registration failed. Email or Username already registered.', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login with role-based session assignment."""
    if request.method == 'POST':
        username = sanitize_user_input(request.form.get('username', ''))
        password = request.form.get('password', '')

        user = db.get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash(f'Logged in successfully as {user["username"]} ({user["role"].capitalize()}).', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Destroy session and log out."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/account', methods=['GET', 'POST'])
def account():
    """Account profile settings manager."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.get_user_by_id(session['user_id'])
    if request.method == 'POST':
        full_name = sanitize_user_input(request.form.get('full_name', ''))
        phone = sanitize_user_input(request.form.get('phone', ''))
        email = sanitize_user_input(request.form.get('email', ''))
        db.update_user_profile(user['id'], full_name, phone, email)
        flash('Account profile updated successfully.', 'success')
        return redirect(url_for('account'))
    return render_template('account.html', user=user)

# --- DASHBOARDS & CORE VIEWS ---

@app.route('/')
def home():
    """Smart Analyzer View & Hero Workspace."""
    weather = get_weather_forecast()
    products = db.get_all_products()[:4]
    return render_template('index.html', weather=weather, products=products)

@app.route('/dashboard')
def dashboard():
    """Role-based master dashboard redirector."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    role = session.get('role', 'farmer')
    if role == 'seller':
        return redirect(url_for('seller_dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('farmer_dashboard'))

@app.route('/farmer/dashboard')
def farmer_dashboard():
    """Farmer Dashboard."""
    user_id = session.get('user_id')
    weather = get_weather_forecast()
    scans = db.get_user_scans(user_id=user_id, limit=5)
    orders = db.get_user_orders(user_id) if user_id else []
    return render_template('farmer_dashboard.html', weather=weather, scans=scans, orders=orders)

@app.route('/seller/dashboard')
def seller_dashboard():
    """Seller Studio Dashboard."""
    if session.get('role') != 'seller' and session.get('role') != 'admin':
        flash('Access restricted to Seller accounts.', 'error')
        return redirect(url_for('login'))
    seller_id = session.get('user_id')
    products = db.get_seller_products(seller_id)
    return render_template('seller_dashboard.html', products=products)

@app.route('/seller/add-product', methods=['POST'])
def add_seller_product():
    """Seller route to post new product."""
    if session.get('role') != 'seller' and session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    name = sanitize_user_input(request.form.get('name'))
    p_type = sanitize_user_input(request.form.get('type', 'organic'))
    target_disease = sanitize_user_input(request.form.get('target_disease', ''))
    price = float(request.form.get('price', 0))
    stock = int(request.form.get('stock', 10))
    description = sanitize_user_input(request.form.get('description', ''))
    usage_steps = sanitize_user_input(request.form.get('usage_steps', ''))
    db.add_product(session['user_id'], name, p_type, target_disease, price, stock, description, usage_steps)
    flash('New Agro-Medicine listed in marketplace.', 'success')
    return redirect(url_for('seller_dashboard'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin Control Panel."""
    if session.get('role') != 'admin':
        flash('Access restricted to System Administrators.', 'error')
        return redirect(url_for('login'))
    all_scans = db.get_user_scans(limit=20)
    all_products = db.get_all_products()
    security_status = check_cia_security_status()
    return render_template('admin_dashboard.html', scans=all_scans, products=all_products, security=security_status)

# --- AI MULTI-IMAGE SCAN & DIAGNOSIS API ---

@app.route('/predict', methods=['POST'])
def predict():
    """Multi-Image Leaf Diagnostic Endpoint."""
    uploaded_files = request.files.getlist('leaf_images')
    if not uploaded_files or len(uploaded_files) == 0 or uploaded_files[0].filename == '':
        return jsonify({'error': 'No image files uploaded'}), 400

    saved_paths = []
    for file in uploaded_files[:3]:
        if file and allowed_file(file.filename):
            timestamp = int(time.time())
            filename = f"leaf_{timestamp}_{secure_filename(file.filename)}"
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            saved_paths.append(filepath)

    if not saved_paths:
        return jsonify({'error': 'Unsupported file format'}), 400

    result = predict_multi_leaf_disease(saved_paths)
    user_id = session.get('user_id')
    rel_path = f"static/uploads/{os.path.basename(saved_paths[0])}"

    scan_id = db.save_scan(
        user_id=user_id,
        filename=os.path.basename(saved_paths[0]),
        image_path=rel_path,
        crop=result['crop'],
        disease=result['disease'],
        label_key=result['label_key'],
        status=result['status'],
        confidence=result['confidence'],
        severity_level=result['severity_level'],
        severity_percent=result['severity_percent'],
        urgency=result['urgency'],
        recovery_time=result['recovery_time'],
        scientific_name=result.get('scientific_name', ''),
        xai_highlights=json.dumps(result['xai_highlights'])
    )

    result['scan_id'] = scan_id
    result['image_path'] = rel_path
    return jsonify(result)

# --- MARKETPLACE, CART & SECURED DIGITAL PAYMENTS ---

@app.route('/marketplace')
def marketplace():
    """Agro-Medicine store catalog."""
    p_type = request.args.get('type')
    search = sanitize_user_input(request.args.get('search'))
    products = db.get_all_products(product_type=p_type, search=search)
    return render_template('marketplace.html', products=products, p_type=p_type, search=search)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page with QR Code and step-by-step usage guide."""
    product = db.get_product_by_id(product_id)
    if not product:
        return "Product not found", 404
    qr_data = generate_product_qr_code(product['id'], product['name'])
    return render_template('product_detail.html', product=product, qr=qr_data)

@app.route('/cart')
def cart():
    """Shopping cart & Checkout view."""
    return render_template('cart.html')

@app.route('/checkout', methods=['POST'])
def checkout():
    """
    CIA Triad Secured Checkout Endpoint.
    Executes Luhn card check / UPI format check, tokenizes payment, and logs transaction.
    """
    if 'user_id' not in session:
        flash('Please login to complete your order.', 'error')
        return redirect(url_for('login'))

    cart_json = request.form.get('cart_data', '[]')
    payment_method = sanitize_user_input(request.form.get('payment_method', 'UPI'))
    shipping_address = sanitize_user_input(request.form.get('shipping_address', 'Default Address'))

    upi_id = sanitize_user_input(request.form.get('upi_id', ''))
    card_number = sanitize_user_input(request.form.get('card_number', ''))

    payment_details = {
        'upi_id': upi_id,
        'card_number': card_number
    }

    try:
        items = json.loads(cart_json)
        if not items:
            flash('Cart is empty.', 'error')
            return redirect(url_for('marketplace'))

        total_amount = sum(item['unit_price'] * item['quantity'] for item in items)

        # Execute CIA Triad Compliant Secured Payment Authorization
        payment_res = process_secure_payment(payment_method, payment_details, total_amount)

        if not payment_res['success']:
            flash(f"Payment Authorization Failed: {payment_res['error_message']}", 'error')
            return redirect(url_for('cart'))

        # Create Order record with masked payment method & transaction receipt ID
        recorded_method = f"{payment_method} ({payment_res['masked_account']}) [Receipt: {payment_res['txn_id']}]"
        order_id = db.create_order(session['user_id'], items, total_amount, recorded_method, shipping_address)

        flash(f"Payment Authorized ({payment_res['txn_id']})! Order #{order_id} placed securely.", 'success')
        return redirect(url_for('orders'))

    except Exception as e:
        flash(f'Checkout Security Error: {e}', 'error')
        return redirect(url_for('cart'))

@app.route('/orders')
def orders():
    """My Orders view with live tracking timeline."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_orders = db.get_user_orders(session['user_id'])
    return render_template('orders.html', orders=user_orders)

@app.route('/cancel-order/<int:order_id>')
def cancel_order(order_id):
    """1-Click Order Cancellation."""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db.update_order_status(order_id, 'Cancelled')
    flash(f'Order #{order_id} has been cancelled.', 'info')
    return redirect(url_for('orders'))

# --- OTHER PLATFORM MODULES ---

@app.route('/farms')
def farms():
    return render_template('farms.html')

@app.route('/soil', methods=['GET', 'POST'])
def soil():
    result = None
    if request.method == 'POST':
        ph = float(request.form.get('ph', 6.5))
        n = float(request.form.get('nitrogen', 150))
        p = float(request.form.get('phosphorus', 30))
        k = float(request.form.get('potassium', 140))
        acres = float(request.form.get('acres', 1.0))
        result = analyze_soil_health(ph, n, p, k, acres)
    return render_template('soil.html', result=result)

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/api/chatbot', methods=['POST'])
def api_chatbot():
    data = request.json or {}
    query = sanitize_user_input(data.get('query', ''))
    lang = sanitize_user_input(data.get('lang', 'en'))
    resp = ask_agribot(query, lang=lang)
    return jsonify(resp)

@app.route('/api/security-audit')
def api_security_audit():
    """Returns live CIA Triad security compliance status."""
    return jsonify(check_cia_security_status())

@app.route('/forum')
def forum():
    return render_template('forum.html')

@app.route('/schemes')
def schemes():
    return render_template('schemes.html')

@app.route('/videos')
def videos():
    return render_template('video_center.html')

@app.route('/history')
def history():
    user_id = session.get('user_id')
    scans = db.get_user_scans(user_id=user_id, limit=100)
    stats = db.get_scan_stats()
    return render_template('history.html', scans=scans, stats=stats)

@app.route('/guide')
def guide():
    return render_template('guide.html', kb=DISEASE_KNOWLEDGE_BASE)

@app.route('/export-report/<int:scan_id>')
def export_report(scan_id):
    scan = db.get_scan_by_id(scan_id)
    if not scan:
        return "Scan report not found.", 404
    info = get_disease_info(scan['label_key'])
    return render_template('report.html', scan=scan, info=info)

if __name__ == '__main__':
    print("============================================================")
    print("PlantaSanitus Smart Agriculture Platform Engine Running")
    print("CIA Triad Secured Payment Gateway Active")
    print("Developed by Rifanshiya J S (Final Year CSE)")
    print("Official Domain: https://plantasanitus.com")
    print("Local Dev Server: http://127.0.0.1:5000")
    print("============================================================")
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ('1', 'true', 'yes')
    app.run(debug=debug, host='0.0.0.0', port=port)
