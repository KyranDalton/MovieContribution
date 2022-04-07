import sqlite3

import click
from flask import g, current_app
from flask.cli import with_appcontext

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def get_db():
    """
    Returns a database connection, creating
    one if one does not already exist in the
    global request object
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def init_db():
    """
    Initializes the database with the defined schema
    """
    db = get_db()

    with current_app.open_resource('schema.sql') as schema_file:
        db.executescript(schema_file.read().decode('utf8'))

def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@click.command('init-db')
@with_appcontext
def init_db_command():
    init_db()
    click.echo('Database initalized')
