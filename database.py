import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.environ.get('PLANTA_DB', 'planta_sanitus.db')

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        email TEXT UNIQUE,
        password_hash TEXT,
        role TEXT,
        full_name TEXT,
        phone TEXT,
        created_at TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        seller_id INTEGER,
        name TEXT,
        type TEXT,
        target_disease TEXT,
        price REAL,
        stock INTEGER,
        description TEXT,
        usage_steps TEXT,
        created_at TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT,
        image_path TEXT,
        crop TEXT,
        disease TEXT,
        label_key TEXT,
        status TEXT,
        confidence REAL,
        severity_level TEXT,
        severity_percent REAL,
        urgency TEXT,
        recovery_time TEXT,
        scientific_name TEXT,
        xai_highlights TEXT,
        created_at TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        items TEXT,
        total_amount REAL,
        payment_method TEXT,
        shipping_address TEXT,
        status TEXT,
        created_at TEXT
    )
    ''')

    conn.commit()
    conn.close()

# Ensure DB initialized on import
init_db()

# --- User helpers ---

def get_user_by_id(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_user_by_username(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def create_user(username, email, password_hash, role='farmer', full_name='', phone=''):
    try:
        conn = get_conn()
        c = conn.cursor()
        now = datetime.utcnow().isoformat()
        c.execute('INSERT INTO users (username,email,password_hash,role,full_name,phone,created_at) VALUES (?,?,?,?,?,?,?)',
                  (username, email, password_hash, role, full_name, phone, now))
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        return user_id
    except Exception:
        return None

def update_user_profile(user_id, full_name, phone, email):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE users SET full_name=?, phone=?, email=? WHERE id=?', (full_name, phone, email, user_id))
    conn.commit()
    conn.close()

# --- Product helpers ---

def get_all_products(product_type=None, search=None):
    conn = get_conn()
    c = conn.cursor()
    query = 'SELECT * FROM products'
    params = []
    where = []
    if product_type:
        where.append('type = ?')
        params.append(product_type)
    if search:
        where.append('(name LIKE ? OR description LIKE ?)')
        params.extend([f'%{search}%', f'%{search}%'])
    if where:
        query += ' WHERE ' + ' AND '.join(where)
    query += ' ORDER BY id DESC'
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_seller_products(seller_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM products WHERE seller_id = ? ORDER BY id DESC', (seller_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_product(seller_id, name, p_type, target_disease, price, stock, description, usage_steps):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    c.execute('INSERT INTO products (seller_id,name,type,target_disease,price,stock,description,usage_steps,created_at) VALUES (?,?,?,?,?,?,?,?,?)',
              (seller_id, name, p_type, target_disease, price, stock, description, usage_steps, now))
    conn.commit()
    pid = c.lastrowid
    conn.close()
    return pid

def get_product_by_id(product_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM products WHERE id = ?', (product_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

# --- Scans & Orders ---

def save_scan(**kwargs):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    fields = [
        'user_id','filename','image_path','crop','disease','label_key','status','confidence',
        'severity_level','severity_percent','urgency','recovery_time','scientific_name','xai_highlights'
    ]
    values = [kwargs.get(f) for f in fields]
    placeholders = ','.join('?' for _ in fields)
    c.execute(f'INSERT INTO scans ({" ,".join(fields)},created_at) VALUES ({placeholders},?)', (*values, now))
    conn.commit()
    sid = c.lastrowid
    conn.close()
    return sid

def get_user_scans(user_id=None, limit=10):
    conn = get_conn()
    c = conn.cursor()
    if user_id:
        c.execute('SELECT * FROM scans WHERE user_id = ? ORDER BY id DESC LIMIT ?', (user_id, limit))
    else:
        c.execute('SELECT * FROM scans ORDER BY id DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_scan_by_id(scan_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM scans WHERE id = ?', (scan_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_scan_stats():
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT disease, COUNT(*) as count FROM scans GROUP BY disease')
    rows = c.fetchall()
    conn.close()
    return {r['disease']: r['count'] for r in rows}

# Orders

def create_order(user_id, items, total_amount, recorded_method, shipping_address):
    conn = get_conn()
    c = conn.cursor()
    now = datetime.utcnow().isoformat()
    items_json = json.dumps(items)
    c.execute('INSERT INTO orders (user_id,items,total_amount,payment_method,shipping_address,status,created_at) VALUES (?,?,?,?,?,?,?)',
              (user_id, items_json, total_amount, recorded_method, shipping_address, 'Placed', now))
    conn.commit()
    oid = c.lastrowid
    conn.close()
    return oid

def get_user_orders(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute('SELECT * FROM orders WHERE user_id = ? ORDER BY id DESC', (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_order_status(order_id, status):
    conn = get_conn()
    c = conn.cursor()
    c.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
    conn.commit()
    conn.close()
