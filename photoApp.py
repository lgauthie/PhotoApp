# all the imports
import os
import sqlite3
from contextlib import closing
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, send_from_directory
from werkzeug import secure_filename

DATABASE = '/tmp/photoApp.db'
UPLOAD_FOLDER = '/tmp/photoAppUploads'
DEBUG = True
SECRET_KEY = 'development key'
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
def home():
    if session['logged_in']:
       return redirect(url_for('user_home', username=str(session['user'])))
    return render_template('home.html')

# Userpage
@app.route('/user/<string:username>')
def user_home(username):
    return render_template('home.html', username=username)

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
            error = 'Invalid username'
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

# Upload Page
@app.route('/upload', methods=['GET','POST'])
def upload():
    error = None
    if request.method == 'POST':
        fileX = request.files['file']
        if fileX and allowed_file(fileX.filename):
            filename = secure_filename(fileX.filename)
            fileX.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
        else:
            flash('Invalid Filename')
    return render_template('upload.html', error=error)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                                   filename)

#@app.route('/upload', methods=['GET', 'POST'])
#def upload():
#    if request.method == 'POST' and 'photo' in request.files:
#        filename = photos.save(request.files['photo'])
#        rec = Photo(filename=filename, user=g.user.id)
#        rec.store()
#        flash("Photo saved.")
#        return redirect(url_for('show', id=rec.id))
#    return render_template('upload.html')
#
#@app.route('/photo/<id>')
#def show(id):
#    photo = Photo.load(id)
#    if photo is None:
#        abort(404)
#    url = photos.url(photo.filename)
#    return render_template('show.html', url=url, photo=photo)

if __name__ == '__main__':
    app.run()
