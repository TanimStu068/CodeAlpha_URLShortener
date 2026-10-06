import re
import secrets
import string
from urllib.parse import urlparse

ALPHABET = string.ascii_letters + string.digits


def generate_code(length=6):
    """Random base62 code, e.g. 'aZ3k9Q'."""
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def is_valid_url(url, max_length=2048):
    """Accept only absolute http/https URLs with a hostname."""
    if not url or len(url) > max_length:
        return False
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def normalize_url(url):
    """Trim whitespace; add https:// when the scheme is missing."""
    url = (url or "").strip()
    # Add https:// only when there is no scheme. "host:8080" is not a scheme,
    # but "javascript:..." is, so it is left alone and rejected by validation.
    has_scheme = re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*:(?!\d)", url)
    if url and not has_scheme:
        url = "https://" + url
    return url
