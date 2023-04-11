import sqlite3

import click
from flask import current_app, g


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

@click.command('populate-posts')
def populate_posts_command():
    """Populate the post table with fake data."""
    from faker import Faker
    fake = Faker()
    db = get_db()

    # Generate 10 fake posts
    for i in range(10):
        title = fake.sentence(nb_words=6)
        author = fake.name()
        created = fake.date_time_between(start_date='-1y', end_date='now')
        content = fake.text()
        db.execute(
            'INSERT INTO post (title, author, created, content) VALUES (?, ?, ?, ?)',
            (title, author, created, content)
        )
        db.commit()

    click.echo('Populated the post table with fake data.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(populate_posts_command)
