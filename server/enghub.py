#!/usr/bin/env python3
"""ENG HUB - portable local server.

Serves the USB folder over http://127.0.0.1:<port> and exposes a tiny API so the
web UI can open worksheets in the machine's associated application.

Works on Windows and Pardus/Linux with nothing but the Python standard library.
"""

import http.server
import json
import os
import socket
import socketserver
import subprocess
import sys
import threading
import urllib.parse
import webbrowser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_PORT = 8777


def pick_port(preferred=DEFAULT_PORT):
    """First free port at or after `preferred`, falling back to any free port."""
    for port in range(preferred, preferred + 40):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def safe_join(rel):
    """Resolve `rel` inside ROOT, or return None if it escapes the USB folder."""
    rel = urllib.parse.unquote(rel or "").lstrip("/\\")
    target = os.path.realpath(os.path.join(ROOT, rel))
    if target == os.path.realpath(ROOT) or target.startswith(os.path.realpath(ROOT) + os.sep):
        return target
    return None


def open_with_os(path):
    """Hand a file to the desktop's associated application."""
    if sys.platform.startswith("win"):
        os.startfile(path)  # noqa: S606 - intentional, this is the whole point
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = dict(http.server.SimpleHTTPRequestHandler.extensions_map)
    extensions_map.update({
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".json": "application/json",
        ".webp": "image/webp",
        ".woff2": "font/woff2",
        ".svg": "image/svg+xml",
    })

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def log_message(self, fmt, *args):
        pass  # keep the console clean for teachers

    def end_headers(self):
        # everything is local; never let a stale copy survive a content refresh
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/ping":
            return self.send_json({"ok": True, "root": ROOT, "platform": sys.platform})
        if parsed.path == "/api/open":
            return self.api_open(parsed)
        if parsed.path == "/api/reveal":
            return self.api_open(parsed, reveal=True)
        resolved = safe_join(parsed.path)
        if resolved and os.path.isfile(resolved):
            return super().do_GET()
        # a missing *file* must stay a 404 - the UI probes for optional JSON
        if os.path.splitext(parsed.path)[1]:
            return self.send_error(404, "File not found")
        # unknown route without an extension -> let the SPA router deal with it
        self.path = "/app/index.html"
        return super().do_GET()

    def send_json(self, payload, code=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def api_open(self, parsed, reveal=False):
        params = urllib.parse.parse_qs(parsed.query)
        target = safe_join((params.get("path") or [""])[0])
        if not target or not os.path.exists(target):
            return self.send_json({"ok": False, "error": "not_found"}, 404)
        try:
            open_with_os(os.path.dirname(target) if reveal else target)
            return self.send_json({"ok": True})
        except Exception as exc:  # pragma: no cover - depends on desktop env
            return self.send_json({"ok": False, "error": str(exc)}, 500)


    # ----------------------------------------------------------- writing back
    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        body = self.rfile.read(length) if length else b""

        if parsed.path == "/api/save":
            return self.api_save(body)
        if parsed.path == "/api/upload":
            return self.api_upload(parsed, body)
        return self.send_json({"ok": False, "error": "unknown_endpoint"}, 404)

    def api_save(self, body):
        """Write an edited slides.json back to the USB (keeps one backup)."""
        try:
            payload = json.loads(body.decode("utf-8"))
            rel, data = payload["path"], payload["data"]
        except (ValueError, KeyError, UnicodeDecodeError) as exc:
            return self.send_json({"ok": False, "error": "bad_payload: %s" % exc}, 400)

        target = safe_join(rel)
        if not target or not target.endswith(".json"):
            return self.send_json({"ok": False, "error": "bad_path"}, 400)

        os.makedirs(os.path.dirname(target), exist_ok=True)
        if os.path.exists(target):
            try:
                with open(target, "rb") as f:
                    prev = f.read()
                with open(target + ".bak", "wb") as f:
                    f.write(prev)
            except OSError:
                pass
        with open(target, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        return self.send_json({"ok": True, "path": rel})

    def api_upload(self, parsed, body):
        """Store a picture the teacher dropped onto a slide."""
        params = urllib.parse.parse_qs(parsed.query)
        rel = (params.get("path") or [""])[0]
        target = safe_join(rel)
        if not target or os.path.splitext(target)[1].lower() not in (
            ".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"
        ):
            return self.send_json({"ok": False, "error": "bad_path"}, 400)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as f:
            f.write(body)
        return self.send_json({"ok": True, "path": rel, "size": len(body)})


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def main():
    port = pick_port(int(os.environ.get("ENGHUB_PORT", DEFAULT_PORT)))
    url = "http://127.0.0.1:%d/" % port
    httpd = Server(("127.0.0.1", port), Handler)

    print("=" * 58)
    print("  ENG HUB calisiyor / running")
    print("  " + url)
    print("  Kapatmak icin bu pencereyi kapatin (Ctrl+C).")
    print("=" * 58)

    if os.environ.get("ENGHUB_NO_BROWSER") != "1":
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nENG HUB kapatildi.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
