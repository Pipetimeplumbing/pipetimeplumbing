import json
import os
import secrets
import sqlite3
from datetime import date
from pathlib import Path
from flask import Flask, jsonify, request

ROOT = Path(__file__).parent
DB = Path(os.environ.get('DATABASE_PATH', str(ROOT / 'data' / 'requests.sqlite')))
DB.parent.mkdir(parents=True, exist_ok=True)
with sqlite3.connect(DB) as db:
    db.execute('CREATE TABLE IF NOT EXISTS requests (id TEXT PRIMARY KEY, kind TEXT, payload TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
app = Flask(__name__, static_folder='public', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 12000

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
    with sqlite3.connect(DB) as db:
        db.execute('INSERT INTO requests(id,kind,payload) VALUES(?,?,?)', (identifier, kind, json.dumps(data)))
    return jsonify(id=identifier), 201

@app.errorhandler(413)
def too_large(error):
    return jsonify(error='Please shorten your request.'), 413
