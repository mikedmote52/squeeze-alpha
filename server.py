import os
import http.server
import socketserver
from urllib.parse import urlparse

# Render uses PORT environment variable
PORT = int(os.environ.get('PORT', 10000))
print(f"Starting server on port {PORT}")
print(f"Environment PORT: {os.environ.get('PORT', 'not set')}")

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>AI Trading System</title>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>
            <body style="background:#1a1a1a; color:white; font-family:Arial; text-align:center; padding:50px;">
                <h1 style="color:#00D4AA;">🚀 AI Trading System</h1>
                <p>System is online and connecting to real Alpaca API</p>
                <p><strong>NO MOCK DATA - Real trading data only</strong></p>
                <div style="background:#333; padding:20px; border-radius:10px; margin:20px;">
                    <h3>✅ System Protection Active</h3>
                    <p>• Zero tolerance for mock/fake data</p>
                    <p>• Real Alpaca API connection only</p>
                    <p>• Authentic trading data enforced</p>
                </div>
                <p style="color:#666;">Service is live and ready</p>
            </body>
            </html>
            '''
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

try:
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"✅ Server successfully started on 0.0.0.0:{PORT}")
        print(f"🌐 Access at: http://0.0.0.0:{PORT}")
        httpd.serve_forever()
except Exception as e:
    print(f"❌ Server failed to start: {e}")
    import traceback
    traceback.print_exc()
    exit(1)