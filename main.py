import os  # 'i' ko small kar diya hai, ab error nahi aayega
from flask import Flask, render_template, request, session, flash, redirect, url_for

app = Flask(__name__)

# Security: Render Dashboard -> Environment Variables mein 'SECRET_KEY' set karein
app.secret_key = os.environ.get("SECRET_KEY", "bhai_ka_permanent_fix_2026")

# -----------------------
# Sample Product Data
# -----------------------
products = [
    {
        "id": 1,
        "name": "iPhone 15 Pro Max",
        "price": "₹1,49,900",
        "image": "iphone15.jpg",
        "description": "Latest Apple iPhone with amazing camera.",
        "amazon_link": "https://www.amazon.in",
        "flipkart_link": "https://www.flipkart.com"
    },
    {
        "id": 2,
        "name": "Samsung Galaxy S23 Ultra",
        "price": "₹1,09,999",
        "image": "galaxy_s23.jpg",
        "description": "High-end Samsung phone with 200MP camera.",
        "amazon_link": "https://www.amazon.in",
        "flipkart_link": "https://www.flipkart.com"
    }
]

# -----------------------
# Routes
# -----------------------

@app.route('/')
def index():
    query = request.args.get('query', '').lower()
    if query:
        filtered_products = [p for p in products if query in p['name'].lower()]
    else:
        filtered_products = products
    return render_template("index.html", products=filtered_products, query=query)

@app.route('/dashboard')
def dashboard():
    if not session.get('username'):
        flash("Please login first")
        return redirect(url_for('login'))
    return render_template("dashboard.html", products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').lower()
        password = request.form.get('password')
        # Simple Check: Email 'admin@example.com' aur Password 'admin'
        if email == "admin@example.com" and password == "admin":
            session['username'] = "Admin"
            flash("Welcome back, Admin!")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password")
    return render_template("login.html")

@app.route('/register')
def register():
    # 'register.html' templates folder mein hona chahiye
    return render_template("register.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully")
    return redirect(url_for('index'))

# -----------------------
# Production Settings
# -----------------------
if __name__ == "__main__":
    # Render dynamic port binding
    port = int(os.environ.get("PORT", 10000))
    # debug=False deployment ke liye permanent setting hai
    app.run(host="0.0.0.0", port=port, debug=False)
