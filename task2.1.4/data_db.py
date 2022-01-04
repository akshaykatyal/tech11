# using sql database to store user related information
import sqlite3

import click
# utilizing the flask application
from flask import current_app, g
from flask.cli import with_appcontext

# function to retrieve data from the database for the user
def user_get():
    if "db" not in g:
        g.db = sqlite3.connect(
            "sqlite_db", detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db
# function to close the database after the data is retrieved or stored
def user_close(e=None):
    db = g.pop("db", None)

    if db is not None:
        db.close()

def init_db():
    db = user_get()
    # reading the database with sql schema
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))

@click.command("init-db")
@with_appcontext
def init_user_command():
    # creating a new table in the database
    init_db()
    click.echo("Table created and database initialized")

def init_app(app):
    app.teardown_appcontext(user_close)
    # function call for initialization
    app.cli.add_command(init_user_command)