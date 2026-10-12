import json
import os
import secrets
import sqlite3
import hashlib
import re
import time
from urllib.parse import urlsplit
from datetime import date
from pathlib import Path
from flask import Flask, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash

ROOT = Path(__file__).parent
DB = Path(os.environ.get('DATABASE_PATH', str(ROOT / 'data' / 'requests.sqlite')))
DB.parent.mkdir(parents=True, exist_ok=True)
with sqlite3.connect(DB) as db:
    db.execute('CREATE TABLE IF NOT EXISTS requests (id TEXT PRIMARY KEY, kind TEXT, payload TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    db.execute('CREATE TABLE IF NOT EXISTS clients (id TEXT PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS sessions (token_hash TEXT PRIMARY KEY, client_id TEXT NOT NULL, expires INTEGER NOT NULL)')
    db.execute('CREATE TABLE IF NOT EXISTS auth_attempts (ip TEXT, timestamp INTEGER)')
    if 'client_id' not in [row[1] for row in db.execute('PRAGMA table_info(requests)')]:
        db.execute('ALTER TABLE requests ADD COLUMN client_id TEXT')
app = Flask(__name__, static_folder='public', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 12000

@app.after_request
def private_responses(response):
    if request.path.startswith(('/api/account', '/api/auth/')):
        response.headers['Cache-Control'] = 'no-store'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

@app.before_request
def protect_mutations():
    if request.method == 'POST':
        origin = request.headers.get('Origin')
        if origin and urlsplit(origin).netloc != request.host:
            return jsonify(error='Request origin not allowed.'), 403
        if not request.is_json:
            return jsonify(error='Send JSON data.'), 415

def current_client():
    token = request.cookies.get('pipe_time_session', '')
    with sqlite3.connect(DB) as db:
        row = db.execute('SELECT clients.id, clients.name, clients.email FROM sessions JOIN clients ON clients.id=sessions.client_id WHERE token_hash=? AND expires>?', (hashlib.sha256(token.encode()).hexdigest(), int(time.time()))).fetchone()
    return dict(zip(('id', 'name', 'email'), row)) if row else None

@app.get('/login')
def login_page():
    return app.send_static_file('login.html')

@app.get('/api/account')
def account():
    client = current_client()
    if not client:
        return jsonify(error='Please sign in.'), 401
    with sqlite3.connect(DB) as db:
        rows = db.execute('SELECT id,kind,payload,created_at FROM requests WHERE client_id=? ORDER BY created_at DESC LIMIT 50', (client['id'],)).fetchall()
    return jsonify(client=client, requests=[dict(id=r[0], kind=r[1], details=json.loads(r[2]), created_at=r[3]) for r in rows])

@app.post('/api/auth/<action>')
def authenticate(action):
    if action == 'logout':
        token = request.cookies.get('pipe_time_session', '')
        with sqlite3.connect(DB) as db:
            db.execute('DELETE FROM sessions WHERE token_hash=?', (hashlib.sha256(token.encode()).hexdigest(),))
        response = jsonify(ok=True)
        response.delete_cookie('pipe_time_session', path='/')
        return response
    if action not in ('login', 'register'):
        return jsonify(error='Not found'), 404
    now = int(time.time())
    ip = request.remote_addr or 'unknown'
    with sqlite3.connect(DB) as db:
        db.execute('DELETE FROM auth_attempts WHERE timestamp<?', (now-900,))
        if db.execute('SELECT COUNT(*) FROM auth_attempts WHERE ip=?', (ip,)).fetchone()[0] >= 15:
            return jsonify(error='Too many attempts. Please try again in 15 minutes.'), 429
        db.execute('INSERT INTO auth_attempts VALUES (?,?)', (ip, now))
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or any(not isinstance(data.get(k), str) for k in ('email', 'password')):
        return jsonify(error='Enter your email and password.'), 400
    email, password = data['email'].strip().lower(), data['password']
    if len(email)>254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email) or not 12<=len(password)<=128:
        return jsonify(error='Use a valid email and a password with 12–128 characters.'), 400
    with sqlite3.connect(DB) as db:
        if action == 'register':
            name = data.get('name', '')
            if not isinstance(name, str) or not 1<=len(name.strip())<=100:
                return jsonify(error='Enter your name (up to 100 characters).'), 400
            client_id = secrets.token_hex(16)
            try:
                db.execute('INSERT INTO clients VALUES (?,?,?,?)', (client_id, name.strip(), email, generate_password_hash(password)))
            except sqlite3.IntegrityError:
                return jsonify(error='Unable to create that account. Try signing in.'), 409
        else:
            row = db.execute('SELECT id,password_hash FROM clients WHERE email=?', (email,)).fetchone()
            valid = check_password_hash(row[1] if row else DUMMY_HASH, password)
            if not row or not valid:
                return jsonify(error='Email or password is incorrect.'), 401
            client_id = row[0]
        token = secrets.token_urlsafe(32)
        db.execute('DELETE FROM sessions WHERE expires<?', (now,))
        db.execute('INSERT INTO sessions VALUES (?,?,?)', (hashlib.sha256(token.encode()).hexdigest(), client_id, now+86400))
    response = jsonify(ok=True)
    response.set_cookie('pipe_time_session', token, max_age=86400, httponly=True, secure=bool(os.environ.get('RENDER')) or request.is_secure, samesite='Lax', path='/')
    return response

DUMMY_HASH = generate_password_hash(secrets.token_urlsafe(32))

@app.get('/')
def home():
    return app.send_static_file('index.html')

@app.get('/health')
def health():
    with sqlite3.connect(DB) as db:
        db.execute('SELECT 1 FROM requests LIMIT 1')
    return jsonify(status='ok')

@app.post('/api/<kind>')
def submit(kind):
    if kind not in ('appointments', 'messages'):
        return jsonify(error='Not found'), 404
    data = request.get_json(silent=True)
    required = ['name', 'phone', 'service', 'date', 'time', 'address'] if kind == 'appointments' else ['name', 'phone', 'message']
    if not isinstance(data, dict) or any(not isinstance(data.get(k), str) or not data[k].strip() for k in required):
        return jsonify(error='Please fill in all required fields.'), 400
    if any(not isinstance(v, str) or len(v) > 3000 for v in data.values()):
        return jsonify(error='Please shorten your request.'), 400
    if len(''.join(c for c in data['phone'] if c.isdigit())) < 10:
        return jsonify(error='Enter a valid phone number with area code.'), 400
    if kind == 'appointments':
        try:
            if date.fromisoformat(data['date']) < date.today():
                raise ValueError()
        except ValueError:
            return jsonify(error='Choose today or a future date.'), 400
    identifier = secrets.token_hex(8)
    client = current_client()
    with sqlite3.connect(DB) as db:
        db.execute('INSERT INTO requests(id,kind,payload,client_id) VALUES(?,?,?,?)', (identifier, kind, json.dumps(data), client['id'] if client else None))
    return jsonify(id=identifier), 201

@app.errorhandler(413)
def too_large(error):
    return jsonify(error='Please shorten your request.'), 413
