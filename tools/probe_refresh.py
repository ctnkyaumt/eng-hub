#!/usr/bin/env python3
"""Validation probe for the root refresh script and server /api/refresh endpoint."""
import http.client
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_root_refresh_script():
    refresh_py = os.path.join(ROOT, "refresh.py")
    assert os.path.isfile(refresh_py), "refresh.py must exist in root"

    # Test importing and finding root
    sys.path.insert(0, ROOT)
    import refresh
    app_root = refresh.find_app_root()
    assert os.path.samefile(app_root, ROOT), f"App root mismatch: {app_root} vs {ROOT}"
    print("[PASS] root refresh.py script exists and finds app root")


def test_g8_u2_books():
    books_path = os.path.join(ROOT, "app", "data", "books.json")
    with open(books_path, "r", encoding="utf-8") as f:
        books = json.load(f)
    g8_u2 = books.get("g8/u2", [])
    assert len(g8_u2) >= 12, f"Expected at least 12 books for g8/u2, got {len(g8_u2)}"
    titles = [b.get("title", "") for b in g8_u2]
    assert any("TEST BOOK" in t.upper() or "BILIM" in t.upper() for t in titles), "G8 U2 books missing expected titles"
    print(f"[PASS] G8 U2 has {len(g8_u2)} books (all 12 verified)")


def test_api_refresh():
    port = 8895
    env = dict(os.environ, ENGHUB_NO_BROWSER="1", ENGHUB_PORT=str(port))
    server_py = os.path.join(ROOT, "server", "enghub.py")
    p = subprocess.Popen([sys.executable, server_py], env=env)
    try:
        # Wait for server
        for _ in range(40):
            time.sleep(0.25)
            try:
                c = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
                c.request("GET", "/api/ping")
                r = c.getresponse()
                if r.status == 200:
                    break
            except (ConnectionRefusedError, OSError):
                continue
        else:
            raise RuntimeError("Server did not start in time")

        # Test POST /api/refresh
        c = http.client.HTTPConnection("127.0.0.1", port, timeout=15)
        c.request("POST", "/api/refresh", body=b"")
        r = c.getresponse()
        assert r.status == 200, f"Expected 200 from /api/refresh, got {r.status}"
        data = json.loads(r.read().decode("utf-8"))
        assert data.get("ok") is True, f"/api/refresh returned ok=False: {data}"
        print("[PASS] POST /api/refresh responded successfully with ok=True")
    finally:
        p.terminate()
        p.wait()


def main():
    test_root_refresh_script()
    test_g8_u2_books()
    test_api_refresh()
    print("ALL REFRESH PROBES PASSED!")


if __name__ == "__main__":
    main()
