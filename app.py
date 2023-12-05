from flask import Flask, request, session, redirect, url_for, render_template, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.secret_key = 'cairocoders-ednalan'

# Configuration for the SQLAlchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:admin@localhost/helpinghand'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the Flask app
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    user_type = db.Column(db.String(50))  

    def __init__(self, fullname, username, password, email, user_type='client'):
        self.fullname = fullname
        self.username = username
        self.password = generate_password_hash(password)
        self.email = email
        self.user_type = user_type

# Home page route
@app.route('/')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('login'))

# Login page route
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['loggedin'] = True
            session['id'] = user.id
            session['username'] = user.username
            return redirect(url_for('home'))
        else:
            flash('Incorrect username/password')
    
    return render_template('login.html')

# Register page route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        user_type = 'worker' if 'Worker' in request.form else 'client'
        
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not fullname or not username or not password or not email:
            flash('Please fill out the form!')
        else:
            new_user = User(fullname=fullname, username=username, password=password, email=email, user_type=user_type)
            db.session.add(new_user)
            db.session.commit()
            flash('You have successfully registered!')
            return redirect(url_for('login'))
    return render_template('register.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# Profile page route
@app.route('/profile')
def profile():
    if 'loggedin' in session:
        user = User.query.filter_by(id=session['id']).first()
        return render_template('profile.html', account=user)
    return redirect(url_for('login'))

# Start the Flask app
if __name__ == "__main__":
    db.create_all()  # Create database tables if they don't exist
    app.run(debug=True)
