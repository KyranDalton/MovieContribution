import functools
import re

from flask import (
    Blueprint,
    flash,
    redirect,
    g,
    render_template,
    request,
    session,
    url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from movie_contribution.database import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")

REGISTER_TEMPLATE = "auth/register.html"
LOGIN_TEMPLATE = "auth/login.html"

@bp.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        db = get_db()
        
        validation_error = _validate_registration(username, email, password)
        if validation_error is not None:
            flash(validation_error, "error")
            return render_template(REGISTER_TEMPLATE)

        try:
            db.execute(
                "INSERT INTO user (username, email, password) VALUES (?, ?, ?)",
                (username, email, generate_password_hash(password)),
            )
            db.commit()
        except db.IntegrityError as er:
            flash(f"User {username} is already registered.", "error")
            return render_template(REGISTER_TEMPLATE)
        else:
            # Success, go to the login page.
            flash("Loging successful", "info")
            return redirect(url_for("auth.login"))
    
    return render_template(REGISTER_TEMPLATE)

@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()

        user = db.execute(
            "SELECT * FROM user WHERE username = ?", (username,)
        ).fetchone()

        if user is None:
            flash("Invalid username or password.", "error")
            return render_template(LOGIN_TEMPLATE)

        if not check_password_hash(user["password"], password):
            flash("Invalid username or password.", "error")
            return render_template(LOGIN_TEMPLATE)

        # Set the session user_id to the logged in user
        # and go back to the home page
        session.clear()
        session["user_id"] = user["user_id"]
        # TODO: Enable this when index is defined
        # return redirect(url_for("index"))

    return render_template(LOGIN_TEMPLATE)

@bp.route("/logout")
def logout():
    session.clear()
    # TODO: Enable this when index is defined
    # return redirect(url_for("index"))
    return redirect(url_for("auth.login"))

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            "SELECT * FROM user WHERE user_id = ?", (user_id,)
        ).fetchone()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)
    return wrapped_view

## Helpers

def _validate_registration(username, email, password):
    username_error = _validate_username(username)
    email_error = _validate_email(email)
    password_error = _validate_password(password)

    return username_error or email_error or password_error

def _validate_username(username):
    if username is None:
        return "Username is required"

def _validate_email(email):
    if email is None:
        return "Email is required"

    emailMatch = re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email)
    if emailMatch is None:
        return "Invalid email"

def _validate_password(password):
    if password is None:
        return "Password is required"

    if len(password) < 8:
        return "Password must be longer than 8 characters"