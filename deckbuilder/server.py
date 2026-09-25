#!/usr/bin/env python3
"""Static file server plus an EDHREC proxy (EDHREC sends no CORS headers)."""
import http.server
import re
import sys
import urllib.request

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        m = re.fullmatch(r"/edhrec/([a-z0-9-]+)", self.path)
        if not m:
            return super().do_GET()
        url = f"https://json.edhrec.com/pages/commanders/{m.group(1)}.json"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "deckbuilder"})
            with urllib.request.urlopen(req, timeout=15) as r:
                body = r.read()
            self.send_response(200)
        except Exception as e:
            body = str(e).encode()
            self.send_response(502)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


http.server.ThreadingHTTPServer(("", PORT), Handler).serve_forever()
