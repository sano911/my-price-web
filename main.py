from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
import time

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey_123")

# Database setup
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- AFFILIATE CONFIG ---
AMAZON_TAG = os.environ.get("AMAZON_TAG", "smartprice-21") 
FLIPKART_AFFID = os.environ.get("FLIPKART_AFFID", "your_affid")

# --- SMART API LOGIC ---
def get_product_data(product):
    api_key = os.environ.get("RAPIDAPI_KEY", "baa2460488msha5e400b4aafc679p14ae78jsnb144d2abc757").strip()
    
    # PEHLA RASTA: Amazon Real-Time API (Fasrt & Accurate)
    # Note: Apne naye Amazon API ka host yahan check karke badlein agar alag hai
    amazon_url = "https://amazon-real-time-product-search.p.rapidapi.com/search" 
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "amazon-real-time-product-search.p.rapidapi.com"
    }
    
    try:
        # Amazon API ko 15s ka time dein
        res = requests.get(amazon_url, headers=headers, params={"q": product, "country": "IN"}, timeout=15)
        if res.status_code == 200:
            data = res.json()
            if data.get('data') and len(data['data']) > 0:
                item = data['data'][0]
                return {
                    "title": item.get('product_title', product.title()),
                    "price": item.get('product_price') or "Check Store",
                    "image": item.get('product_photo', "https://via.placeholder.com/250"),
                    "amazon_link": f"{item.get('product_url')}&tag={AMAZON_TAG}",
                    "flipkart_link": f"https://www.flipkart.com/search?q={product}&affid={FLIPKART_AFFID}",
                    "is_fallback": False
                }
    except Exception as e:
        print(f"Amazon API Error: {e}")

    # DUSRA RASTA: Real-Time Product Search (Pichli Wali API)
    # Agar Amazon API fail ho jaye, toh ise call karein
    fallback_url = "https://real-time-product-search.p.rapidapi.com/search"
    headers_fb = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "real-time-product-search.p.rapidapi.com"
    }
    
    try:
        res_fb = requests.get(fallback_url, headers=headers_fb, params={"q": product, "country": "in"}, timeout=25)
        if res_fb.status_code == 200:
            data_fb = res_fb.json()
            if data_fb.get('data') and len(data_fb['data']) > 0:
                item = data_fb['data'][0]
                return {
                    "title": item.get('product_title', product.title()),
                    "price": item.get('product_price') or "Check Store",
                    "image": item.get('product_photos', ["https://via.placeholder.com/250"])[0],
                    "amazon_link": f"https://www.amazon.in/s?k={product}&tag={AMAZON_TAG}",
                    "flipkart_link": f"https://www.flipkart.com/search?q={product}&affid={FLIPKART_AFFID}",
                    "is_fallback": False
                }
    except Exception as e:
        print(f"Fallback API Error: {e}")

    return None

@app.route("/", methods=["GET", "POST"])
def home():
    product_data = None
    if request.method == "POST":
        product = request.form.get("product")
        if product:
            product_data = get_product_data(product)
            # TEESRA RASTA: Dono API fail hone par Affiliate Link dikhao
            if not product_data:
                product_data = {
                    "title": product.title(),
                    "price": "Live Price Unavailable",
                    "image": "https://via.placeholder.com/250?text=Search+Results",
                    "amazon_link": f"https://www.amazon.in/s?k={product}&tag={AMAZON_TAG}",
                    "flipkart_link": f"https://www.flipkart.com/search?q={product}&affid={FLIPKART_AFFID}",
                    "is_fallback": True
                }
    return render_template("index.html", product_data=product_data)

# ... (baaki routes register/login purane hi rakhein) ...

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
