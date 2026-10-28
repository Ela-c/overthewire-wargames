from http.server import HTTPServer, BaseHTTPRequestHandler

class OOBHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress default noisy access logs to keep stdout clean for exfiltrated data
        return

    def do_GET(self):
        print(f"\n[+] GET Request Received:")
        print(f"Path / Data: {self.path}")
        print(f"Headers:\n{self.headers}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8', errors='ignore')
        print(f"\n[+] POST Request Received:")
        print(f"Path: {self.path}")
        print(f"Headers:\n{self.headers}")
        print(f"Body / Exfiltrated Data:\n{body}")
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

if __name__ == '__main__':
    port = 8080
    server_address = ('', port)
    httpd = HTTPServer(server_address, OOBHandler)
    print(f"[*] Custom HTTP Listener running on port {port}...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down listener.")
        httpd.server_close()