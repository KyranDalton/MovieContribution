DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS director;
DROP TABLE IF EXISTS movie;

CREATE TABLE user (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE director (
    director_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE movie (
    movie_id INTEGER PRIMARY KEY AUTOINCREMENT,
    movie_title TEXT NOT NULL,
    plot TEXT NOT NULL,
    director INTEGER NOT NULL,
    added_by INTEGER NOT NULL,
    FOREIGN KEY (director) REFERENCES director(director_id),
    FOREIGN KEY (added_by) REFERENCES user(user_id)
);
