# all the imports
import unicodedata
import sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash

DATABASE = '/tmp/photoApp.db'
DEBUG = True
SECRET_KEY = 'development key'
USERS = {'admin':'default','leesifer':'password12345'}
CURRENT_USER = None
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

def normstr(string):
    if type(string) == str:
        unicodedata.normalize('NFKD', string).encode('ascii','ignore')


# Close the connection when leaving
@app.teardown_request
def teardown_request(exception):
    g.db.close()

# Root Page, shows entries
@app.route('/')
def home():
#    query = """select title, text, id
#               from entries
#               order by id desc"""
#    cur = g.db.execute(query)
#    entries = [dict(title=row[0], text=row[1], id=row[2]) for row in cur.fetchall()]
    return render_template('home.html')

# The login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        query = """
                select password
                from users
                where username = ( ? )
                """
        value = [request.form['username']]
        cur = g.db.execute(query, value)
        val = cur.fetchone()
        if not val:
            error = 'Incalid username'
            return render_template('login.html', error=error)

        entry = str(val[0])

        if not request.form['password'] == entry:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            session['user'] = request.form['username']
            flash(session['user'] + ' You were logged in')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)

# The logout
@app.route('/logout')
def logout():
    session['logged_in'] = False
    session['user']= None
    flash('You were logged out')
    return redirect(url_for('home'))

# The page for creating a user
@app.route('/create_user', methods=['GET','POST'])
def create_user():
    error = None
    if request.method == 'POST':
        query = """select username
                   from users
                   where username = ( ? )"""
        value = [request.form['create_username']]
        cur = g.db.execute(query, value)
        username = cur.fetchone()

        if username:
            flash('Username Taken')
        elif(request.form['create_password'] == request.form['check_password']):
            query = """
                    insert into users (username, password)
                    values (?, ?)

                    """
            values = [request.form['create_username'],request.form['create_password']]
            g.db.execute(query, values)
            flash('Sucess!')
            flash('User: ' + request.form['create_username'] + ' created')
        else:
            flash('Passwords dont match')
        g.db.commit()
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET','POST'])
def upload():
    error = None
    return render_template('create_user.html', error=error)

if __name__ == '__main__':
    app.run()
