import os
import tempfile

import pytest

from movie_contribution import create_app
from movie_contribution.database import get_db
from movie_contribution.database import init_db

# read in SQL for populating test data
with open(os.path.join(os.path.dirname(__file__), "test_data.sql"), "rb") as sql_file:
    _test_data_sql = sql_file.read().decode("utf8")

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    # create the app with common test config
    app = create_app({ "TESTING": True, "DATABASE": db_path })

    # initialize the database and load test data
    with app.app_context():
        init_db()
        get_db().executescript(_test_data_sql)

    yield app

    # close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")

@pytest.fixture
def auth(client):
    return AuthActions(client)
