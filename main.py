from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests
from requests.exceptions import RequestException

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey_123")  # Render pe env var set karo

# Database setup (SQLite for simplicity, production mein PostgreSQL use karo)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Agar login route hai to

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Affiliate tags from env (Render dashboard mein add karo)
AMAZON_TAG = os.environ.get("AMAZON_TAG", "smartprice-21")
FLIPKART_AFFID = os.environ.get("FLIPKART_AFFID", "your_affid_here")

# RapidAPI Key (Render env mein set karo - sensitive hai!)
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")

# Headers for all API calls
HEADERS = {
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": ""  # endpoint ke hisaab se update hoga
}

def get_product_data(query):
    if not RAPIDAPI_KEY:
        print("Warning: RAPIDAPI_KEY not set in environment variables!")
        return None

    # Option 1: Real-Time Amazon Data API (best for Amazon prices)
    try:
        amazon_host = "real-time-amazon-data.p.rapidapi.com"
        amazon_url = f"https://{amazon_host}/search"
        HEADERS["X-RapidAPI-Host"] = amazon_host

        params = {
            "query": query,
            "country": "IN",
            "sort_by": "RELEVANCE",  # ya "PRICE_LOW_TO_HIGH" etc.
            "page": "1"
        }

        response = requests.get(amazon_url, headers=HEADERS, params=params, timeout=12)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "OK" and data.get("data") and len(data["data"]) > 0:
            item = data["data"][0]
            price_str = item.get("product_price_current", {}).get("price", "Check Store")
            if price_str and isinstance(price_str, str):
                price_str = price_str.replace("₹", "").replace(",", "").strip()
            return {
                "title": item.get("product_title", query.title()),
                "price": f"₹{price_str}" if price_str != "Check Store" else "Check Store",
                "image": item.get("product_main_image_url") or item.get("product_photos", ["https://via.placeholder.com/300"])[0],
                "amazon_link": f"{item.get('product_url')}&tag={AMAZON_TAG}" if item.get('product_url') else f"https://www.amazon.in/s?k={query}&tag={AMAZON_TAG}",
                "flipkart_link": f"https://www.flipkart.com/search?q={query}&affid={FLIPKART_AFFID}",
                "source": "Amazon API",
                "is_fallback": False
            }
    except RequestException as e:
        print(f"Amazon API failed: {e}")

    # Option 2: General Real-Time Product Search (Google Shopping based - covers Flipkart etc.)
    try:
        general_host = "real-time-product-search.p.rapidapi.com"
        general_url = f"https://{general_host}/search"
        HEADERS["X-RapidAPI-Host"] = general_host

        params = {
            "q": query,
            "country": "in",
            "limit": "1"  # sirf best match
        }

        response = requests.get(general_url, headers=HEADERS, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == "OK" and data.get("data") and len(data["data"]) > 0:
            item = data["data"][0]
            price = item.get("product_price") or "Check Store"
            return {
                "title": item.get("product_title", query.title()),
                "price": price,
                "image": item.get("product_photos", ["https://via.placeholder.com/300"])[0] if item.get("product_photos") else "https://via.placeholder.com/300",
                "amazon_link": f"https://www.amazon.in/s?k={query}&tag={AMAZON_TAG}",
                "flipkart_link": f"https://www.flipkart.com/search?q={query}&affid={FLIPKART_AFFID}",
                "source": "General Product Search",
                "is_fallback": False
            }
    except RequestException as e:
        print(f"General API failed: {e}")

    # Final fallback: Just affiliate links
    return {
        "title": query.title(),
        "price": "Live Price Unavailable",
        "image": "https://via.placeholder.com/300?text=No+Image+Found",
        "amazon_link": f"https://www.amazon.in/s?k={query}&tag={AMAZON_TAG}",
        "flipkart_link": f"https://www.flipkart.com/search?q={query}&affid={FLIPKART_AFFID}",
        "source": "Fallback",
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
            flash("Please enter a product name!", "error")

    return render_template("index.html", product_data=product_data)

# Add your other routes here (login, register, dashboard, logout etc.)
# Example placeholder:
@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

# Create DB tables
with app.app_context():
    db.create_all()

# For local testing
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render uses $PORT, local 5000
    app.run(host="0.0.0.0", port=port, debug=True)
