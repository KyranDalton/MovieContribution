from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    url_for
)
from werkzeug.exceptions import abort

from movie_contribution.auth import login_required
from movie_contribution.database import get_db

bp = Blueprint("movie", __name__)

ADD_TEMPLATE = "movie/add.html"
UPDATE_TEMPLATE = "movie/update.html"

@bp.route("/")
@login_required
def index():
    db = get_db()
    movies = db.execute(
        "SELECT movie_id, movie_title, plot, created, username "
        "FROM movie m JOIN user u ON m.added_by = u.user_id "
        "ORDER BY created DESC"
    ).fetchall()
    return render_template("movie/index.html", movies=movies)

@bp.route("/add", methods=("GET", "POST"))
@login_required
def add():
    if request.method == "POST":
        movie_title = request.form["movie_title"]
        plot = request.form["plot"]

        validation_error = _validate_movie_request(movie_title, plot)

        if validation_error is not None:
            flash(validation_error, "error")
            return render_template(ADD_TEMPLATE)

        db = get_db()
        db.execute(
            "INSERT INTO movie (movie_title, plot, added_by)"
            "VALUES (?, ?, ?)",
            (movie_title, plot, g.user["user_id"])
        )
        db.commit()
        return redirect(url_for("movie.index"))

    return render_template(ADD_TEMPLATE)


@bp.route("/<int:movie_id>/update", methods=("GET", "POST"))
@login_required
def update(movie_id):
    movie = _get_movie(movie_id)

    if request.method == "POST":
        movie_title = request.form["movie_title"]
        plot = request.form["plot"]

        validation_error = _validate_movie_request(movie_title, plot)

        if validation_error is not None:
            flash(validation_error, "error")
            return render_template(UPDATE_TEMPLATE)

        db = get_db()
        db.execute(
            "UPDATE movie SET movie_title = ?, plot = ?"
            "WHERE movie_id = ?",
            (movie_title, plot, movie_id)
        )
        db.commit()
        return redirect(url_for("movie.index"))

    return render_template("movie/update.html", movie=movie)

@bp.route("/<int:movie_id>/delete", methods=("POST",))
@login_required
def delete(movie_id):
    _get_movie(movie_id)

    user_is_admin = g.user['is_admin']

    if not user_is_admin:
        abort(403)

    db = get_db()
    db.execute("DELETE FROM movie WHERE movie_id = ?", (movie_id,))
    db.commit()

    return redirect(url_for("movie.index"))

# Helpers

def _get_movie(movie_id):
    movie = get_db().execute(
        "SELECT movie_id, movie_title, plot, created, username "
        "FROM movie m JOIN user u ON m.added_by = u.user_id "
        "WHERE m.movie_id = ?",
        (movie_id,)
    ).fetchone()

    if movie is None:
        abort(404, f"Movie {id} does not exist.")

    return movie

def _validate_movie_request(movie_title, plot):
    if movie_title is None:
        return "Movie title is required"

    if plot is None:
        return "Movie plot is required"
