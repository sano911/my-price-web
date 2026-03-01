from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "YOUR_SECRET_KEY"

# Sample product data (replace with DB or API later)
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
    },
    {
        "name": "OnePlus 11",
        "price": "₹49,999",
        "image": "oneplus11.jpg",
        "description": "Fast performance and smooth display.",
        "amazon_link": "https://www.amazon.in/dp/B0ZZZZZZ",
        "flipkart_link": "https://www.flipkart.com/item?pid=ZZZZZ"
    }
]

# -------------------
# ROUTES
# -------------------

@app.route('/')
def index():
    # Homepage: show product cards + search bar
    query = request.args.get('query', '').lower()
    filtered_products = products
    if query:
        filtered_products = [p for p in products if query in p['name'].lower()]
    return render_template("index.html", products=filtered_products, query=query)

@app.route('/dashboard')
def dashboard():
    # Optional: show most viewed / top products
    return render_template("dashboard.html", products=products)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']
        # Temporary in-memory login
        if email == "admin@example.com" and password == "admin":
            session['username'] = "Admin"
            flash("Login successful")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials")
            return redirect(url_for('login'))
    return render_template("login.html")

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        flash("Registration feature coming soon")
        return redirect(url_for('login'))
    return render_template("register.html")

@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully")
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
