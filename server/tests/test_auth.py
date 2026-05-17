import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import auth


def setup_temp_token():
    """Override TOKEN_FILE to use a temp file for testing."""
    tmp = tempfile.NamedTemporaryFile(suffix=".token", delete=False)
    tmp.close()
    os.unlink(tmp.name)  # Remove so init_auth creates it fresh
    auth.TOKEN_FILE = tmp.name
    return tmp.name


def teardown_temp_token(path: str):
    if os.path.exists(path):
        os.unlink(path)


def test_init_auth_generates_token():
    path = setup_temp_token()
    token = auth.init_auth()
    assert token != ""
    assert len(token) > 20
    assert os.path.exists(path)
    teardown_temp_token(path)


def test_init_auth_second_call_returns_empty():
    path = setup_temp_token()
    auth.init_auth()
    second = auth.init_auth()
    assert second == ""
    teardown_temp_token(path)


def test_verify_token_valid():
    path = setup_temp_token()
    token = auth.init_auth()
    assert auth.verify_token(token) is True
    teardown_temp_token(path)


def test_verify_token_invalid():
    path = setup_temp_token()
    auth.init_auth()
    assert auth.verify_token("wrong-token-here") is False
    teardown_temp_token(path)


def test_reset_token():
    path = setup_temp_token()
    old_token = auth.init_auth()
    new_token = auth.reset_token()
    assert new_token != ""
    assert new_token != old_token
    assert auth.verify_token(new_token) is True
    assert auth.verify_token(old_token) is False
    teardown_temp_token(path)


def test_hash_token_deterministic():
    h1 = auth._hash_token("test123")
    h2 = auth._hash_token("test123")
    assert h1 == h2


def test_hash_token_different_inputs():
    h1 = auth._hash_token("token_a")
    h2 = auth._hash_token("token_b")
    assert h1 != h2
