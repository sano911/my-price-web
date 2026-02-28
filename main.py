from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
import time

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey_123")

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# ---------------- DATABASE MODEL ----------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------- AFFILIATE CONFIG ----------------
AMAZON_TAG = os.environ.get("AMAZON_TAG", "smartprice-21") 
FLIPKART_AFFID = os.environ.get("FLIPKART_AFFID", "your_affid")

# ---------------- UPGRADED PRODUCT FUNCTION ----------------
def get_product_data(product):
    url = "https://real-time-product-search.p.rapidapi.com/search"
    querystring = {"q": product, "country": "in", "language": "en"}
    
    # Aapka dashboard dikha raha hai ki response slow hai (22s)
    # Isliye hum timeout 30 seconds rakhenge
    api_key = os.environ.get("RAPIDAPI_KEY", "baa2460488msha5e400b4aafc679p14ae78jsnb144d2abc757").strip()

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "real-time-product-search.p.rapidapi.com"
    }

    # Retry logic: Agar pehli baar mein data na mile (Empty Body)
    for attempt in range(2):
        try:
            response = requests.get(url, headers=headers, params=querystring, timeout=30)
            if response.status_code == 200:
                data = response.json()
                # 2 Bytes body size fix: Check karein ki real data hai ya nahi
                if data.get('data') and len(data['data']) > 0:
                    item = data['data'][0]
                    raw_url = item.get('product_url', '')
                    
                    # Affiliate Link Logic
                    amazon_aff_link = f"{raw_url}&tag={AMAZON_TAG}" if "amazon.in" in raw_url else f"https://www.amazon.in/s?k={product}&tag={AMAZON_TAG}"
                    flipkart_aff_link = f"https://www.flipkart.com/search?q={product}&affid={FLIPKART_AFFID}"
                    
                    return {
                        "title": item.get('product_title', product.title()),
                        "price": item.get('offer', {}).get('price') or item.get('product_price') or "Check Store",
                        "image": item.get('product_photos', ["https://via.placeholder.com/250"])[0],
                        "amazon_link": amazon_aff_link,
                        "flipkart_link": flipkart_aff_link,
                        "is_fallback": False
                    }
            # Agar data empty hai (2 bytes), thoda ruk kar dubara try karein
            time.sleep(1) 
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
    
    return None

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    product_data = None
    trending_deals = [
        {"name": "iPhone 15", "img": "https://m.media-amazon.com/images/I/71d7rfSl0wL._SL1500_.jpg"},
        {"name": "Samsung S24", "img": "https://m.media-amazon.com/images/I/71R6C6n5EFL._SL1500_.jpg"},
        {"name": "MacBook Air", "img": "https://m.media-amazon.com/images/I/71ItM9kooLL._SL1500_.jpg"}
    ]
    
    if request.method == "POST":
        product = request.form.get("product")
        if product:
            product_data = get_product_data(product)
            if not product_data:
                product_data = {
                    "title": product.title(),
                    "price": "Check Current Price",
                    "image": "https://via.placeholder.com/250?text=Check+Offers",
                    "amazon_link": f"https://www.amazon.in/s?k={product}&tag={AMAZON_TAG}",
                    "flipkart_link": f"https://www.flipkart.com/search?q={product}&affid={FLIPKART_AFFID}",
                    "is_fallback": True
                }
    return render_template("index.html", product_data=product_data, trending_deals=trending_deals)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])
        if User.query.filter_by(username=username).first():
            flash("User already exists!")
            return redirect(url_for("register"))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful!")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid Credentials!")
    return render_template("login.html")

@app.route("/dashboard")
@login_required
def dashboard():
    users = User.query.all()
    return render_template("dashboard.html", users=users)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
