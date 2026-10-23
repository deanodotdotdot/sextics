#!/usr/bin/env python3
"""Build and watch local records, then serve this checkout on loopback only."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import threading

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--port', type=int, default=8765)
parser.add_argument('--no-watch', action='store_true')
args = parser.parse_args()
stop = threading.Event()

def build():
    result = subprocess.run([sys.executable, str(ROOT / 'scripts/build-content.py')], capture_output=True, text=True)
    print((result.stdout if result.returncode == 0 else 'Content update rejected; keeping the last successful build.\n' + result.stderr).strip(), flush=True)
    return result.returncode == 0

def source_stamp():
    paths = [ROOT / 'index.html', ROOT / 'data/catalogue.json', ROOT / 'docs/index.json', ROOT / 'scripts/build-content.py', ROOT / 'scripts/content.py']
    for pattern in ['data/*/*.rec', 'data/*/*.md', 'data/*/witness.json', 'data/*/provenance.json', 'docs/*.md', 'assets/*.js', 'assets/*.css']:
        paths.extend(ROOT.glob(pattern))
    result = []
    for path in sorted(set(paths)):
        try:
            stat = path.stat()
            result.append((str(path), stat.st_mtime_ns, stat.st_size))
        except FileNotFoundError:
            result.append((str(path), None, None))
    return result

def watch():
    previous = source_stamp()
    while not stop.wait(.75):
        current = source_stamp()
        if current != previous:
            # Wait for a brief quiet interval so a saved group of edits is one build.
            if stop.wait(.35): return
            previous = source_stamp()
            build()

class Handler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()
    def log_message(self, format, *values):
        # Polling and successful asset requests do not drown out build diagnostics.
        if len(values) > 1 and values[1] not in ('200', '304'):
            super().log_message(format, *values)

if not build():
    raise SystemExit('Fix the content error before starting the preview.')
server = ThreadingHTTPServer(('127.0.0.1', args.port), partial(Handler, directory=str(ROOT)))
if not args.no_watch:
    threading.Thread(target=watch, daemon=True).start()
print(f'Local preview: http://127.0.0.1:{args.port}/ (record changes refresh automatically)', flush=True)
try:
    server.serve_forever()
except KeyboardInterrupt:
    pass
finally:
    stop.set()
    server.server_close()
