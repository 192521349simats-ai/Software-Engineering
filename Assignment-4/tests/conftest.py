import sys
from pathlib import Path
import pytest

BACKEND_PATH = str(Path(__file__).resolve().parents[1] / "backend")
if BACKEND_PATH not in sys.path:
    sys.path.insert(0, BACKEND_PATH)

import app as app_module

flask_app = app_module.app
init_db = app_module.init_db


@pytest.fixture
def client(tmp_path, monkeypatch):
    test_db = str(tmp_path / "test_campus.db")
    init_db(test_db)
    monkeypatch.setattr(app_module, "DB_PATH", test_db)

    flask_app.config["TESTING"] = True

    with flask_app.test_client() as test_client:
        yield test_client
