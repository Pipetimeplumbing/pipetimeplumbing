import json, os, secrets, sqlite3
from pathlib import Path
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from datetime import date

ROOT = Path(__file__).parent
DB = ROOT / 'data' / 'requests.sqlite'
DB.parent.mkdir(exist_ok=True)
with sqlite3.connect(DB) as db:
    db.execute('CREATE TABLE IF NOT EXISTS requests (id TEXT PRIMARY KEY, kind TEXT, payload TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP)')

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / 'public'), **kwargs)
    def do_POST(self):
        if self.path not in ('/api/appointments', '/api/messages'):
            return self.reply(404, {'error': 'Not found'})
        try:
            size = int(self.headers.get('Content-Length', 0))
            if not 0 < size <= 12000:
                raise ValueError('Please shorten your request.')
            data = json.loads(self.rfile.read(size))
            required = ['name', 'phone', 'service', 'date', 'time', 'address'] if self.path.endswith('appointments') else ['name', 'phone', 'message']
            if not isinstance(data, dict) or any(not isinstance(data.get(k), str) or not data[k].strip() for k in required):
                raise ValueError('Please fill in all required fields.')
            if any(not isinstance(v, str) or len(v) > 3000 for v in data.values()):
                raise ValueError('Please shorten your request.')
            if len(''.join(c for c in data['phone'] if c.isdigit())) < 10:
                raise ValueError('Enter a valid phone number with area code.')
            if 'date' in data and date.fromisoformat(data['date']) < date.today():
                raise ValueError('Choose today or a future date.')
            identifier = secrets.token_hex(8)
            with sqlite3.connect(DB) as db:
                db.execute('INSERT INTO requests(id,kind,payload) VALUES(?,?,?)', (identifier, self.path.split('/')[-1], json.dumps(data)))
            self.reply(201, {'id': identifier})
        except (ValueError, TypeError, json.JSONDecodeError) as error:
            self.reply(400, {'error': str(error)})
    def reply(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == '__main__':
    ThreadingHTTPServer(('0.0.0.0', int(os.environ.get('PORT', '3000'))), Handler).serve_forever()
