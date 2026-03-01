import os
from flask import Flask, render_template, request, session, flash, redirect, url_for

app = Flask(__name__)

# Security Tip: Render Dashboard mein 'SECRET_KEY' naam ka Env Var banayein
app.secret_key = os.environ.get("SECRET_KEY", "default_fallback_key_123")

# -----------------------
# Sample Product Data
# -----------------------
products = [
    {
        "name": "iPhone 15 Pro Max",
        "price": "₹1,49,900",
        "image": "iphone15.jpg",
        "description": "Latest Apple iPhone with amazing camera.",
        "amazon_link": "https://www.amazon.in/dp/B0XXXXXXX",
        "flipkart_link": "https://www.flipkart.com/item?pid=XXXXX"
    },
    {
        "name": "Samsung Galaxy S23 Ultra",
        "price": "₹1,09,999",
        "image": "galaxy_s23.jpg",
        "description": "High-end Samsung phone with 200MP camera.",
        "amazon_link": "https://www.amazon.in/dp/B0YYYYYYY",
        "flipkart_link": "https://www.flipkart.com/item?pid=YYYYY"
    }
]

# -----------------------
# Routes
# -----------------------

@app.route('/')
def index():
    query = request.args.get('query', '').lower()
    filtered_products = [p for p in products if query in p['name'].lower()] if query else products
    return render_template("index.html", products=filtered_products, query=query)

@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html", products=products)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').lower()
        password = request.form.get('password')
        if email == "admin@example.com" and password == "admin":
            session['username'] = "Admin"
            flash("Login successful")
            return redirect(url_for('dashboard'))
        flash("Invalid credentials")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully")
    return redirect(url_for('index'))

# -----------------------
# Production Port Binding
# -----------------------
if __name__ == "__main__":
    # Render dynamic port assign karta hai, isliye os.environ.get zaroori hai
    port = int(os.environ.get("PORT", 10000))
    # host="0.0.0.0" hona chahiye taaki bahar se traffic aa sake
    app.run(host="0.0.0.0", port=port)
