import pytest
from flask import g, session

from movie_contribution.database import get_db
from movie_contribution.movie import _get_movie, _validate_movie_request

def test_index_suceeds(client, auth):
    response = client.get("/")

    # Make sure we redirect to the login page for auth
    expected_location = "/auth/login"
    actual_location = response.headers["Location"]

    assert expected_location == actual_location

    auth.login()
    response = client.get("/")
    assert response.status_code == 200


def test_add_succeeds(client, app, auth):
    auth.login()

    response = client.post("/add", data={
        "movie_title": "test title",
        "plot": "my cool plot"
    })

    # Check we redirected to the index page
    expected_location = "/"
    actual_location = response.headers["Location"]

    assert expected_location == actual_location

    # Check we added data to the DB
    with app.app_context():
        assert (
            get_db().execute("SELECT * FROM movie WHERE movie_title = 'test title'").fetchone()
            is not None
        )


def test_update_succeeds(client, app, auth):
    auth.login()

    response = client.post("/1/update", data={
        "movie_title": "A Test Movie",
        "plot": "A new plot for A Test Movie"
    })

    # Check we redirected to the index page
    expected_location = "/"
    actual_location = response.headers["Location"]

    assert expected_location == actual_location

    # Check we updated data the DB
    with app.app_context():
        movie = get_db().execute("SELECT * FROM movie WHERE movie_id = 1").fetchone()
        assert movie["movie_title"] == "A Test Movie" # Does not change
        assert movie["plot"] == "A new plot for A Test Movie" # Does change


def test_delete_error_not_admin(client, auth, app):
    auth.login()

    response = client.post("/1/delete")

    assert response.status_code == 403

    # Check we didn't delete the data in the DB
    with app.app_context():
        count = get_db().execute("SELECT COUNT(*) FROM movie").fetchone()[0]
        assert count == 1

def test_delete_succeeds(client, auth, app):
    auth.login('other', 'other')

    response = client.post("/1/delete")

    # Check we redirected to the index page
    expected_location = "/"
    actual_location = response.headers["Location"]

    assert expected_location == actual_location

    # Check we deleted the data in the DB
    with app.app_context():
        count = get_db().execute("SELECT COUNT(*) FROM movie").fetchone()[0]
        assert count == 0


def test_validate_movie_request_no_title():
    validation_error = _validate_movie_request(None, "A fake plot")
    assert validation_error == "Movie title is required"

def test_validate_move_request_no_plot():
    validation_error = _validate_movie_request("A Test Title", None)
    assert validation_error == "Movie plot is required"

def test_validate_movie_request_succeeds():
    validation_error = _validate_movie_request("A Test Title", "A fake plot")
    assert validation_error is None
