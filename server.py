import os
import json
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

PORT = int(os.environ.get('PORT', 8080))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(BASE_DIR, "server_save.json")

class FarmServerHandler(SimpleHTTPRequestHandler):
    extensions_map = SimpleHTTPRequestHandler.extensions_map.copy()
    extensions_map.update({
        '.json': 'application/json',
        '.webmanifest': 'application/manifest+json',
        '.js': 'application/javascript',
        '.ico': 'image/x-icon',
        '.png': 'image/png',
        '.svg': 'image/svg+xml',
    })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        path_clean = self.path.split('?')[0].rstrip('/')
        if path_clean == '/api/load':
            if os.path.exists(SAVE_FILE):
                try:
                    with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                        data = f.read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json; charset=utf-8')
                    self.send_header('Cache-Control', 'no-cache')
                    self.end_headers()
                    self.wfile.write(data.encode('utf-8'))
                    return
                except Exception as e:
                    print(f"Error reading server save: {e}", flush=True)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "no_save"}).encode('utf-8'))
            return

        super().do_GET()

    def do_POST(self):
        path_clean = self.path.split('?')[0].rstrip('/')
        if path_clean == '/api/save':
            try:
                content_len = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_len)
                data = json.loads(body.decode('utf-8'))

                with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

                resp = json.dumps({
                    "status": "ok",
                    "savedAt": data.get("savedAt", 0),
                    "serverTime": os.path.getmtime(SAVE_FILE)
                })
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(resp.encode('utf-8'))
                return
            except Exception as e:
                print(f"Error saving to server: {e}", flush=True)
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode('utf-8'))
                return

        if path_clean == '/api/reset':
            if os.path.exists(SAVE_FILE):
                try:
                    os.remove(SAVE_FILE)
                except Exception as e:
                    print(f"Error removing save file: {e}", flush=True)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "reset"}).encode('utf-8'))
            return

        self.send_response(404)
        self.end_headers()

if __name__ == '__main__':
    os.chdir(BASE_DIR)
    server = HTTPServer(('0.0.0.0', PORT), FarmServerHandler)
    print(f"[OK] Cozy Hay Farm 3D Server running on http://localhost:{PORT}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...", flush=True)
        server.server_close()
