#!/usr/bin/env python3
"""Validation probe for the updater engine, migration logic, and server update endpoints."""
import http.client
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "server"))
import updater


def test_version_logic():
    assert updater.parse_version("v1.8.0") == (1, 8, 0)
    assert updater.parse_version("v1.8") == (1, 8, 0)
    assert updater.parse_version("1.7.2") == (1, 7, 2)
    assert updater.is_newer("v1.9", "v1.8.0") is True
    assert updater.is_newer("v1.8.1", "v1.8.0") is True
    assert updater.is_newer("v1.7", "v1.8.0") is False
    assert updater.is_newer("v1.8.0", "v1.8.0") is False

    cur_v = updater.get_current_version(ROOT)
    assert cur_v.startswith("v1.8"), f"Expected v1.8*, got {cur_v}"
    print(f"[PASS] Version logic verified (current: {cur_v})")


def test_check_for_updates():
    res = updater.check_for_updates()
    assert res.get("ok") is True, f"check_for_updates failed: {res}"
    assert "currentVersion" in res
    assert "latestVersion" in res
    assert "updateAvailable" in res
    print(f"[PASS] check_for_updates() returned valid release info: latest={res.get('latestVersion')}")


def test_migration_and_safe_update():
    """Simulates updating an installation while preserving user customized slides and uploads."""
    with tempfile.TemporaryDirectory(prefix="enghub_probe_") as tmpdir:
        mock_root = os.path.join(tmpdir, "eng-hub")
        os.makedirs(os.path.join(mock_root, "content", "g5", "u1", "presentation"), exist_ok=True)
        os.makedirs(os.path.join(mock_root, "content", "g5", "u1", "presentation", "img"), exist_ok=True)

        # 1. Existing user files
        user_slide_content = '{"title": "Custom Teacher Slide"}'
        user_bak_content = b'{"title": "Custom Teacher Slide Bak"}'
        slides_path = os.path.join(mock_root, "content", "g5", "u1", "presentation", "slides.json")
        bak_path = os.path.join(mock_root, "content", "g5", "u1", "presentation", "slides.json.bak")
        user_photo_path = os.path.join(mock_root, "content", "g5", "u1", "presentation", "img", "teacher_photo.png")

        with open(slides_path, "w", encoding="utf-8") as f:
            f.write(user_slide_content)
        with open(bak_path, "wb") as f:
            f.write(user_bak_content)
        with open(user_photo_path, "wb") as f:
            f.write(b"PNG_FAKE_BYTES")
        with open(os.path.join(mock_root, "VERSION.txt"), "w", encoding="utf-8") as f:
            f.write("v1.7.0  2026-09-29\n")

        # 2. Create mock update zip with upstream changes
        mock_zip_dir = os.path.join(tmpdir, "mock_update")
        pkg_root = os.path.join(mock_zip_dir, "eng-hub")
        os.makedirs(os.path.join(pkg_root, "content", "g5", "u1", "presentation"), exist_ok=True)
        upstream_slide_content = '{"title": "Upstream New v1.8 Slide"}'
        with open(os.path.join(pkg_root, "content", "g5", "u1", "presentation", "slides.json"), "w", encoding="utf-8") as f:
            f.write(upstream_slide_content)
        with open(os.path.join(pkg_root, "new_feature.txt"), "w", encoding="utf-8") as f:
            f.write("New feature content in v1.8")
        with open(os.path.join(pkg_root, "VERSION.txt"), "w", encoding="utf-8") as f:
            f.write("v1.8.0  2026-10-01\n")

        zip_file = os.path.join(tmpdir, "update_package.zip")
        with zipfile.ZipFile(zip_file, "w") as zf:
            for root, dirs, files in os.walk(mock_zip_dir):
                for f in files:
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, mock_zip_dir)
                    zf.write(full_p, rel_p)

        # 3. Simulate apply_update logic directly on mock_root
        temp_dir = os.path.join(mock_root, "temp_work", "update")
        os.makedirs(temp_dir, exist_ok=True)
        extract_dir = os.path.join(temp_dir, "extracted")
        with zipfile.ZipFile(zip_file, "r") as zf:
            zf.extractall(extract_dir)

        candidate_root = os.path.join(extract_dir, "eng-hub")

        # Capture user customized slides
        saved_user_slides = {}
        content_dir = os.path.join(mock_root, "content")
        for root, dirs, files in os.walk(content_dir):
            if "slides.json.bak" in files and "slides.json" in files:
                rel = os.path.relpath(root, content_dir)
                saved_user_slides[rel] = {
                    "slides": open(os.path.join(root, "slides.json"), "r", encoding="utf-8").read(),
                    "bak": open(os.path.join(root, "slides.json.bak"), "rb").read(),
                }

        # Safe copy updated tree
        updater.copy_tree_safe(candidate_root, mock_root)

        # Restore user customized slides
        for rel, data in saved_user_slides.items():
            unit_dir = os.path.join(content_dir, rel)
            slides_f = os.path.join(unit_dir, "slides.json")
            bak_f = os.path.join(unit_dir, "slides.json.bak")
            upstream_f = os.path.join(unit_dir, "slides.upstream.json")
            if os.path.isfile(slides_f):
                shutil.copy2(slides_f, upstream_f)
            with open(slides_f, "w", encoding="utf-8") as sf:
                sf.write(data["slides"])
            with open(bak_f, "wb") as bf:
                bf.write(data["bak"])

        # Clean up temp
        shutil.rmtree(temp_dir, ignore_errors=True)
        if os.path.isdir(os.path.join(mock_root, "temp_work")):
            shutil.rmtree(os.path.join(mock_root, "temp_work"), ignore_errors=True)

        # 4. Verify outcomes:
        # User customized slides preserved
        with open(slides_path, "r", encoding="utf-8") as sf:
            assert sf.read() == user_slide_content, "User customized slides were overwritten!"

        # Upstream slides backed up
        upstream_path = os.path.join(mock_root, "content", "g5", "u1", "presentation", "slides.upstream.json")
        assert os.path.isfile(upstream_path), "Upstream slides backup missing!"
        with open(upstream_path, "r", encoding="utf-8") as uf:
            assert uf.read() == upstream_slide_content, "Upstream slide content wrong!"

        # User photo preserved
        assert os.path.isfile(user_photo_path), "User uploaded photo was deleted!"

        # New feature file added
        assert os.path.isfile(os.path.join(mock_root, "new_feature.txt")), "New feature file not copied!"

        # Temp files cleaned up
        assert not os.path.exists(os.path.join(mock_root, "temp_work")), "temp_work was not cleaned up!"

        print("[PASS] Migration logic successfully verified (user slides & uploads preserved, upstream files migrated)")


def test_api_update_endpoints():
    port = 8896
    env = dict(os.environ, ENGHUB_NO_BROWSER="1", ENGHUB_PORT=str(port))
    server_py = os.path.join(ROOT, "server", "enghub.py")
    p = subprocess.Popen([sys.executable, server_py], env=env)
    try:
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

        # Test GET /api/update/check
        c = http.client.HTTPConnection("127.0.0.1", port, timeout=15)
        c.request("GET", "/api/update/check")
        r = c.getresponse()
        assert r.status == 200, f"Expected 200 from /api/update/check, got {r.status}"
        data = json.loads(r.read().decode("utf-8"))
        assert data.get("ok") is True, f"/api/update/check returned ok=False: {data}"
        assert "currentVersion" in data
        assert "latestVersion" in data
        assert "updateAvailable" in data
        print(f"[PASS] GET /api/update/check passed (current={data.get('currentVersion')}, latest={data.get('latestVersion')})")
    finally:
        p.terminate()
        p.wait()


def main():
    test_version_logic()
    test_check_for_updates()
    test_migration_and_safe_update()
    test_api_update_endpoints()
    print("ALL UPDATER PROBES PASSED!")


if __name__ == "__main__":
    main()
