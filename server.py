#!/usr/bin/env python3
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import os
os.chdir(Path(__file__).resolve().parent)
class Handler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args): pass
server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
print("Open http://127.0.0.1:8000")
try: server.serve_forever()
except KeyboardInterrupt: pass
finally: server.server_close()
