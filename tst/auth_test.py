import pytest
from flask import g, session

from movie_contribution.database import get_db
from movie_contribution.auth import (
    _validate_registration,
    _validate_username,
    _validate_email,
    _validate_password
)

import json

def test_registration_validation_failed(client, app):
    response = client.post("auth/register", data={
        "username": "abc",
        "email": "invalid email",
        "password": "abcdefgh"
    })

    # Make sure we don't redirect
    assert "Location" not in response.headers

    # Check the flashed message
    assert b"Invalid email" in response.data

    # Make sure we didn't write to the DB
    with app.app_context():
        assert (
            get_db().execute("SELECT * FROM user WHERE username = 'abc'").fetchone()
            is None
        )

def test_registration_existing_username(client, app):
    response = client.post("auth/register", data={
        "username": "test",
        "email": "abc@tes.com",
        "password": "abcdefgh"
    })

    # Make sure we don't redirect
    assert "Location" not in response.headers

    # Check the flashed message
    assert b"User test is already registered." in response.data

    # Make sure we didn't write to the DB
    with app.app_context():
        assert (
            get_db().execute("SELECT * FROM user WHERE username = 'abc'").fetchone()
            is None
        )

def test_registration_successful_not_admin(client, app):
    response = client.post("/auth/register", data={
        "username": "abc",
        "email": "abc@email.com",
        "password": "abcdefgh"
    })

    # Make sure we redirect to the login page
    expected_location = "/auth/login"
    actual_location = response.headers["Location"]

    assert expected_location == actual_location

    # Make sure we wrote to the DB
    with app.app_context():
        user = get_db().execute("SELECT * FROM user WHERE username = 'abc'").fetchone()
        assert user is not None
        assert user['is_admin'] == 0

def test_registration_successful_is_admin(client, app):
    response = client.post("/auth/register", data={
        "username": "abc",
        "email": "abc@imdb.com",
        "password": "abcdefgh"
    })

    # Make sure we redirect to the login page
    expected_location = "/auth/login"
    actual_location = response.headers["Location"]

    assert expected_location == actual_location

    # Make sure we wrote to the DB
    with app.app_context():
        user = get_db().execute("SELECT * FROM user WHERE username = 'abc'").fetchone()
        assert user is not None
        assert user['is_admin'] == 1


def test_login_incorrect_username(client):
    response = client.post("/auth/login", data={
        "username": "unknown",
        "password": "12345678"
    })

    # Check the flashed message
    assert b"Invalid username or password." in response.data

    with client.session_transaction() as client_session:
        # Make sure we haven't signed in
        assert "user_id" not in client_session

def test_login_incorrect_password(client):
    response = client.post("/auth/login", data={
        "username": "test",
        "password": "incorrect"
    })

    # Check the flashed message
    assert b"Invalid username or password." in response.data

    with client.session_transaction() as client_session:
        # Make sure we haven't signed in
        assert "user_id" not in client_session

def test_login_successful(client):
    client.post("/auth/login", data={
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
