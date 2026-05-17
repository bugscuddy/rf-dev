import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import db


def setup_temp_db():
    """Override DB_PATH to use a temp file for testing."""
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db.DB_PATH = tmp.name
    db.init_db()
    return tmp.name


def teardown_temp_db(path: str):
    """Clean up temp database."""
    if os.path.exists(path):
        os.unlink(path)


def test_init_db_creates_tables():
    path = setup_temp_db()
    import sqlite3
    conn = sqlite3.connect(path)
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    table_names = [t[0] for t in tables]
    assert "metrics" in table_names
    assert "events" in table_names
    conn.close()
    teardown_temp_db(path)


def test_log_metric():
    path = setup_temp_db()
    db.log_metric(1.5, 99.0, is_gateway=True)
    db.log_metric(0.8, 95.0, is_gateway=False)
    
    history = db.get_metrics_history(30)
    assert len(history) == 2
    assert history[0]["gb_shared"] == 1.5
    assert history[0]["is_gateway"] is True
    assert history[1]["gb_shared"] == 0.8
    assert history[1]["is_gateway"] is False
    teardown_temp_db(path)


def test_get_metrics_history_limit():
    path = setup_temp_db()
    for i in range(10):
        db.log_metric(float(i), 90.0 + i)
    
    history = db.get_metrics_history(5)
    assert len(history) == 5
    teardown_temp_db(path)


def test_get_metrics_history_empty():
    path = setup_temp_db()
    history = db.get_metrics_history(30)
    assert history == []
    teardown_temp_db(path)
