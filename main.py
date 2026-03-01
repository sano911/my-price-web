from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # production me strong key use karo

# In-memory DB (replace with real DB in production)
users_db = {}

# Pass current year to templates
@app.context_processor
def inject_year():
    return {'current_year': datetime.now().year}

# -------------------
# Routes
# -------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip().lower()
        password = request.form['password']

        if email in users_db:
            flash("Email already registered!")
            return redirect(url_for('register'))

        users_db[email] = {'username': username, 'password': generate_password_hash(password)}
        flash("Registration successful! Please login.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password']

        user = users_db.get(email)
        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            session['email'] = email
            flash("Login successful!")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password!")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash("Please login to access dashboard.")
        return redirect(url_for('login'))

    total_visits = 123
    profile_completion = 85
    unread_messages = 5
    return render_template('dashboard.html',
                           total_visits=total_visits,
                           profile_completion=profile_completion,
                           unread_messages=unread_messages)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('index'))

# For local development only
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
