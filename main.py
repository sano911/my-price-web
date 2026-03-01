import os
from flask import Flask, render_template, request, session, flash, redirect, url_for

app = Flask(__name__)
# Render Dashboard se SECRET_KEY lega, nahi toh default use karega
app.secret_key = os.environ.get("SECRET_KEY", "bhai_ka_final_fix_2026")

# --- Temporary Database (Isme naye users save honge) ---
# Format: {"email": "password"}
users = {"admin@example.com": "admin"} 

# --- Featured Products (Homepage ke liye) ---
featured_products = [
    {
        "name": "iPhone 15 Pro Max",
        "price": "₹1,49,900",
        "image": "iphone15.jpg",
        "description": "Latest Apple flagship with Titanium design.",
        "amazon_link": "https://www.amazon.in/s?k=iphone+15+pro+max",
        "flipkart_link": "https://www.flipkart.com/search?q=iphone+15+pro+max"
    },
    {
        "name": "Samsung Galaxy S23 Ultra",
        "price": "₹1,09,999",
        "image": "galaxy_s23.jpg",
        "description": "High-end Samsung phone with S-Pen.",
        "amazon_link": "https://www.amazon.in/s?k=samsung+s23+ultra",
        "flipkart_link": "https://www.flipkart.com/search?q=samsung+s23+ultra"
    }
]

# -----------------------
# HOME & SEARCH ROUTE
# -----------------------
@app.route('/')
def index():
    query = request.args.get('query', '').strip()
    
    if query:
        # 1. Pehle featured list mein check karo
        results = [p for p in featured_products if query.lower() in p['name'].lower()]
        
        # 2. Agar list mein nahi hai -> Universal Redirect Card banao
        if not results:
            dynamic_product = {
                "name": query.title(),
                "price": "Check Live Store",
                "image": "default.jpg", 
                "description": f"Best deals for '{query}' found on top stores.",
                "amazon_link": f"https://www.amazon.in/s?k={query.replace(' ', '+')}",
                "flipkart_link": f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
            }
            results = [dynamic_product]
    else:
        results = featured_products

    return render_template("index.html", products=results, query=query)

# -----------------------
# LOGIN ROUTE (FIXED)
# -----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password')
        
        # Check database
        if email in users and users[email] == password:
            session['username'] = email
            flash("Login Successful! Welcome back.")
            return redirect(url_for('index'))
        else:
            flash("Galti! Email ya Password galat hai.")
            
    return render_template("login.html")

# -----------------------
# REGISTER ROUTE (FIXED)
# -----------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').lower().strip()
        password = request.form.get('password')
        
        if not email or not password:
            flash("Please fill all fields!")
        elif email in users:
            flash("Email pehle se register hai. Login karein.")
        else:
            # Naya user save ho raha hai
            users[email] = password
            flash("Registration Successful! Ab Login karein.")
            return redirect(url_for('login'))
            
    return render_template("register.html")

# -----------------------
# LOGOUT ROUTE
# -----------------------
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('index'))

# -----------------------
# RENDER DEPLOYMENT SETTINGS
# -----------------------
if __name__ == "__main__":
    # Render dynamic port binding
    port = int(os.environ.get("PORT", 10000))
    # host 0.0.0.0 is mandatory for Render/Cloud
    app.run(host="0.0.0.0", port=port, debug=False)
