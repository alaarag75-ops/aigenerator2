from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.request import urlopen, Request
from urllib.parse import urlparse, parse_qs
import json

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/api/proxy'):
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            target = params.get('url', [None])[0]
            if not target:
                self._json(400, {'status': False, 'message': 'missing url'})
                return
            try:
                req = Request(target, headers={'User-Agent': 'Mozilla/5.0'})
                with urlopen(req, timeout=180) as r:
                    body = r.read()
                self._json(200, body, raw=True)
            except Exception as e:
                self._json(500, {'status': False, 'message': str(e)})
            return
        super().do_GET()

    def _json(self, code, data, raw=False):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(data if raw else json.dumps(data).encode())

print('🚀 Serving on http://localhost:8080')
HTTPServer(('', 8080), Handler).serve_forever()
