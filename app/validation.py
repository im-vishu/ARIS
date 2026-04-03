from urllib.parse import urlparse
from email.utils import parseaddr
from datetime import datetime

def is_valid_url(url: str) -> bool:
    try:
        p = urlparse(url)
        return p.scheme in ("http", "https") and bool(p.netloc)
    except Exception:
        return False

def is_valid_email(addr: str) -> bool:
    return "@" in parseaddr(addr)[1]

def is_valid_iso_datetime(dt: str) -> bool:
    try:
        datetime.fromisoformat(dt)
        return True
    except Exception:
        return False