# all the imports
import sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash

DATABASE = '/tmp/photoApp.db'
DEBUG = True
SECRET_KEY = 'development key'
USERS = {'admin':'default','leesifer':'password12345'}
USERNAME = 'admin'
PASSWORD = 'default'
UPLOAD_FOLDER = '/tmp/photoUploads'
ALLOWED_EXTENSIONS = set(['png','jpg','gif'])

app = Flask(__name__)
app.config.from_object(__name__)

# Connect to the database
# Currently a sqlite3 database
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

# Initialize the database
# This should probably be moved to a different
# file at some point.
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()

# Connect to the database when accessing a page
@app.before_request
def before_request():
    g.db = connect_db()

# Close the connection when leaving
@app.teardown_request
def teardown_request(exception):
    g.db.close()

# Root Page, shows entries
@app.route('/')
def show_entries():
#    query = """select title, text, id
#               from entries
#               order by id desc"""
#    cur = g.db.execute(query)
#    entries = [dict(title=row[0], text=row[1], id=row[2]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

# The login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if not request.form['username'] in app.config['USERS']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['USERS'][request.form['username']]:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash(app.config['USERS'][request.form['username']] + ' You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

