import pytest
from flask import g, session

from movie_contribution.database import get_db
from movie_contribution.auth import (
    _validate_registration,
    _validate_username,
    _validate_email,
    _validate_password
)

def test_registration_validation_failed(client, app):
    response = client.post("auth/register", data={
        "username": "abc",
        "email": "invalid email",
        "password": "abcdefgh"
    })

    # Make sure we don't redirect
    assert "Location" not in response.headers

    # Make sure we didn't write to the DB
    with app.app_context():
        assert (
            get_db().execute("SELECT * FROM user WHERE username = 'abc'").fetchone()
            is None
        )

    # Check the flashed message
    with client.session_transaction() as client_session:
        flash_message = dict(client_session["_flashes"]).get("error")
        assert "Invalid email" == flash_message

def test_registration_existing_username(client, app):
    response = client.post("auth/register", data={
        "username": "test",
        "email": "abc@tes.com",
        "password": "abcdefgh"
    })

    # Make sure we don't redirect
    assert "Location" not in response.headers

    # Make sure we didn't write to the DB
    with app.app_context():
        assert (
            get_db().execute("SELECT * FROM user WHERE username = 'abc'").fetchone()
            is None
        )

    # Check the flashed message
    with client.session_transaction() as client_session:
        flash_message = dict(client_session["_flashes"]).get("error")
        assert "User test is already registered." == flash_message

def test_registration_successful(client, app):
    response = client.post("/auth/register", data={
        "username": "abc",
        "email": "abc@email.com",
        "password": "abcdefgh"
    })
    
    # Make sure we redirect to the login page
    expectedLocation = "/auth/login"
    actualLocation = response.headers["Location"]

    assert expectedLocation == actualLocation

    # Make sure we wrote to the DB
    with app.app_context():
        assert (
            get_db().execute("SELECT * FROM user WHERE username = 'abc'").fetchone()
            is not None
        )


def test_login_incorrect_username(client):
    response = client.post("/auth/login", data={
        "username": "unknown",
        "password": "12345678"
    })

    with client.session_transaction() as client_session:
        # Check flashed message
        flash_message = dict(client_session["_flashes"]).get("error")
        assert "Invalid username or password." == flash_message
        # Make sure we haven't signed in
        assert "user_id" not in client_session

def test_login_incorrect_password(client):
    response = client.post("/auth/login", data={
        "username": "test",
        "password": "incorrect"
    })

    with client.session_transaction() as client_session:
        # Check flashed message
        flash_message = dict(client_session["_flashes"]).get("error")
        assert "Invalid username or password." == flash_message
        # Make sure we haven't signed in
        assert "user_id" not in client_session

def test_login_successful(client):
    response = client.post("/auth/login", data={
        "username": "test",
        "password": "test"
    })

    with client.session_transaction() as client_session:
        # Make sure we've signed in
        assert "user_id" in client_session


def test_logout(client, auth):
    auth.login()

    with client.session_transaction() as client_session:
        # Check the user_id is in the session beforehand
        assert "user_id" in client_session

    auth.logout()

    with client.session_transaction() as client_session:
        # Check the user_id is cleared
        assert "user_id" not in client_session


def test_validate_registration_invalid_username():
    validation_error = _validate_registration(None, "test@imdb.com", "12345678")
    assert "Username is required" == validation_error

def test_validate_registration_invalid_email():
    validation_error = _validate_registration("ABC", "invalid email", "12345678")
    assert "Invalid email" == validation_error

def test_validate_registration_invalid_password():
    validation_error = _validate_registration("ABC", "test@imdb.com", "1")
    assert "Password must be longer than 8 characters" == validation_error

def test_validate_registration_valid_request():
    validation_error = _validate_registration("ABC", "test@imdb.com", "12345678")
    assert validation_error is None


def test_validate_email_no_email():
    validation_error = _validate_email(None)
    assert "Email is required" == validation_error

def test_validate_email_invalid_email():
    validation_error = _validate_email("invalid")
    assert "Invalid email" == validation_error

def test_validate_email_valid_email():
    validation_error = _validate_email("test@imdb.com")
    assert validation_error is None
    

def test_validate_password_no_password():
    validation_error = _validate_password(None)
    assert "Password is required" == validation_error

def test_validate_password_invalid_password():
    validation_error = _validate_password("123")
    assert "Password must be longer than 8 characters" == validation_error

def test_validate_password_valid_password():
    validation_error = _validate_password("12345678")
    assert validation_error is None
