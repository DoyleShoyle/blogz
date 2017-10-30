from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "abc"

class Blog(db.Model):      

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    body = db.Column(db.String(1200))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):     

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __repr__(self):
        return self.username



def validate_username(username):
    if len(username) >= 3 and len(username) < 20:
        if " " not in username:
            return False
        else:
            username_error = True
            flash('Spaces are not allowed in username!', 'error')
            username = ''
            return username_error
    else:
        username_error = True
        flash('Username must be between 3 and 20 characters long!', 'error')
        username = ""
        return username_error

def validate_password(password, verify):
    if len(password) >= 3 and len(password) <= 20:
        if " " not in password:
            if password == verify:
                return False
            else:
                password_error = True
                flash('Passwords do not match!', 'error')
                return password_error
        else:
            password_error = True
            flash('Spaces are not allowed in password!', 'error')
            return password_error
    else:
        password_error = True
        flash('Password must be between 3 and 20 characters long!', 'error')
        return password_error




@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        flash('You must be logged in', 'error')
        return redirect('/login')



@app.route('/', methods=['GET'])
def index():
    users = User.query.all()
    id = request.query_string
    if request.method == 'GET':
        if not id:
            return render_template('index.html', users=users)
        else:
            user = test
            blog = test

            return render_template('singleuser.html', user=user, blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if not title:
            flash('Title cannot be blank.')
            return redirect('/newpost')
        if not body:
            flash('Enter a blog')
            return redirect('/newpost')

        else:
            new_post = Blog(title, body, owner)
            db.session.add(new_post)
            db.session.commit()
            id = str(new_post.id)
            return redirect('/blogz?b='+ id)


        return redirect('/blogz')

    return render_template('newpost.html')

@app.route('/blogz', methods=['POST', 'GET'])
def blog():
    blogs = Blog.query.all()
    owner = Blog.query.all()
    id = request.query_string
    if request.method == 'GET':
        if not id:
            return render_template('blog.html', blogs=blogs, owner=owner)
        else:
            if "b=" in str(id):
                b = int(request.args.get('b'))
                blog = Blog.query.get(b)
                return render_template('singlepost.html', blog=blog)
            if "user=" in str(id):
                user = request.args.get('user')
                owner = User.query.filter_by(username=user).first()
                blogs = Blog.query.filter_by(owner_id=owner.id).all()
                return render_template('singleuser.html', blogs=blogs)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        username_error = validate_username(username)
        password_error = validate_password(password, verify)

        if not username_error and not password_error:
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                flash('This user already exists', 'error')

    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in", 'error')
            return redirect('/newpost')
        if not user:
            flash('Invalid username', 'error')
        else:
            flash('Incorrect password', 'error')

    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    del session['username']
    return redirect('/blogz')

if __name__ == '__main__':
    app.run()
