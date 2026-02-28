from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests

app = Flask(__name__)
# Secret key ko environment variable se uthayein ya default rakhein
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")

# Database config - SQLite deployment ke liye thik hai
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

# ---------------- PRODUCT FUNCTION ----------------
def get_product_data(product):
    url = "https://real-time-product-search.p.rapidapi.com/search"
    
    querystring = {
        "q": product,
        "country": "in",
        "language": "en"
    }

    # API key ko environment variable se uthana best hai, 
    # varna ye direct key bhi kaam karegi (lekin secure nahi hai)
    api_key = os.environ.get("RAPIDAPI_KEY", "baa2460488msha5e400b4aafc679p14ae78jsnb144d2abc757")

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "real-time-product-search.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        data = response.json()
        
        if data.get('data') and len(data['data']) > 0:
            item = data['data'][0]
            return {
                "title": item.get('product_title', product.title()),
                "price": item.get('offer', {}).get('price', "Check on Store"),
                "image": item.get('product_photos', ["https://via.placeholder.com/250"])[0],
                "amazon_link": item.get('product_url', f"https://www.amazon.in/s?k={product}"),
                "flipkart_link": f"https://www.flipkart.com/search?q={product}"
            }
    except Exception as e:
        print(f"API Error: {e}")
    
    return None

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET", "POST"])
def home():
    product_data = None
    if request.method == "POST":
        product = request.form.get("product")
        if product:
            product_data = get_product_data(product)
    return render_template("index.html", product_data=product_data)

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
        flash("Registration successful! Please login.")
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
        else:
            flash("Invalid username or password!")
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

# ---------------- DEPLOYMENT SETTINGS ----------------
# Is block ke bina Render par tables nahi banenge
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
