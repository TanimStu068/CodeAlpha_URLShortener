import os
import sys
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import create_app  # noqa: E402


@pytest.fixture
def client():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    app = create_app({"DATABASE": path, "TESTING": True})
    yield app.test_client()
    os.remove(path)


def test_shorten_and_redirect(client):
    r = client.post("/api/shorten", json={"url": "https://example.com/long/path"})
    assert r.status_code == 201
    code = r.get_json()["short_code"]
    assert len(code) == 6

    r = client.get(f"/{code}")
    assert r.status_code == 302
    assert r.headers["Location"] == "https://example.com/long/path"


def test_same_url_returns_same_code(client):
    a = client.post("/api/shorten", json={"url": "https://example.com"}).get_json()
    b = client.post("/api/shorten", json={"url": "https://example.com"}).get_json()
    assert a["short_code"] == b["short_code"]


def test_missing_scheme_is_normalized(client):
    r = client.post("/api/shorten", json={"url": "example.com"})
    assert r.get_json()["original_url"] == "https://example.com"


@pytest.mark.parametrize("bad", ["", "javascript:alert(1)", "ftp://x.com", "http://"])
def test_invalid_urls_rejected(client, bad):
    assert client.post("/api/shorten", json={"url": bad}).status_code == 400


def test_unknown_code_404(client):
    assert client.get("/nope123").status_code == 404


def test_click_counter(client):
    code = client.post("/api/shorten", json={"url": "https://example.com"}).get_json()["short_code"]
    client.get(f"/{code}")
    client.get(f"/{code}")
    assert client.get(f"/api/stats/{code}").get_json()["clicks"] == 2
