from app.safety import is_blocked, is_allowed, requires_confirmation

def test_blocked_command():
    assert is_blocked("rm -rf /") is True

def test_allowed_simple():
    assert is_allowed("echo hello") is True

def test_disallowed():
    assert is_allowed("net user newadmin") is False

def test_confirmation():
    assert requires_confirmation("pip install requests") is True