from flask import Flask, render_template, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
from requests.exceptions import RequestException, Timeout
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey_123")  # Render pe env var set kar lo

# Database config (SQLite local, Render pe PostgreSQL better hota hai)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///database.db")
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

# Affiliate tags (env se lo)
AMAZON_TAG = os.environ.get("AMAZON_TAG", "smartprice-21")
FLIPKART_AFFID = os.environ.get("FLIPKART_AFFID", "your_affid_here")

# RapidAPI Key
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")

# Context processor for current year (footer ke liye)
@app.context_processor
def inject_current_year():
    return dict(current_year=datetime.now().year)

def get_product_data(query):
    if not RAPIDAPI_KEY:
        print("RAPIDAPI_KEY missing in environment variables!")
        return None

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": ""
    }

    # 1. Amazon specific API (better price accuracy)
    try:
        host = "real-time-amazon-data.p.rapidapi.com"
        url = f"https://{host}/search"
        headers["X-RapidAPI-Host"] = host

        params = {"query": query, "country": "IN", "page": "1"}
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "OK" and data.get("data") and len(data["data"]) > 0:
            item = data["data"][0]
            price = item.get("product_price_current", {}).get("price", "Check Store")
            if price and isinstance(price, str):
                price = price.replace("₹", "").replace(",", "").strip()
            return {
                "title": item.get("product_title", query.title()),
                "price": f"₹{price}" if price != "Check Store" else "Check Store",
                "image": item.get("product_main_image_url") or "https://via.placeholder.com/300",
                "amazon_link": f"{item.get('product_url')}&tag={AMAZON_TAG}" if item.get('product_url') else f"https://www.amazon.in/s?k={query}&tag={AMAZON_TAG}",
                "flipkart_link": f"https://www.flipkart.com/search?q={query}&affid={FLIPKART_AFFID}",
                "is_fallback": False
            }
    except (RequestException, Timeout) as e:
        print(f"Amazon API error: {e}")

    # 2. General product search fallback
    try:
        host = "real-time-product-search.p.rapidapi.com"
        url = f"https://{host}/search"
        headers["X-RapidAPI-Host"] = host

        params = {"q": query, "country": "in", "limit": "1"}
        response = requests.get(url, headers=headers, params=params, timeout=12)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "OK" and data.get("data") and len(data["data"]) > 0:
            item = data["data"][0]
            return {
                "title": item.get("product_title", query.title()),
                "price": item.get("product_price") or "Check Store",
                "image": item.get("product_photos", ["https://via.placeholder.com/300"])[0],
                "amazon_link": f"https://www.amazon.in/s?k={query}&tag={AMAZON_TAG}",
                "flipkart_link": f"https://www.flipkart.com/search?q={query}&affid={FLIPKART_AFFID}",
                "is_fallback": False
            }
    except (RequestException, Timeout) as e:
        print(f"General API error: {e}")

    # Final fallback
    return {
        "title": query.title(),
        "price": "Live Price Unavailable",
        "image": "https://via.placeholder.com/300?text=No+Image",
        "amazon_link": f"https://www.amazon.in/s?k={query}&tag={AMAZON_TAG}",
        "flipkart_link": f"https://www.flipkart.com/search?q={query}&affid={FLIPKART_AFFID}",
        "is_fallback": True
    }

@app.route("/", methods=["GET", "POST"])
def home():
    product_data = None
    if request.method == "POST":
        product = request.form.get("product", "").strip()
        if product:
            product_data = get_product_data(product)
        else:
            flash("Product name ya link daalo bhai!", "error")

    return render_template("index.html", product_data=product_data)

# Baaki routes (login, register, dashboard, logout) yahan add karna
# Example placeholder:
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# Database tables create
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
