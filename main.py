import os  # 'i' small rakha hai taaki crash na ho
from flask import Flask, render_template, request, session, flash, redirect, url_for

app = Flask(__name__)
# Render Dashboard mein 'SECRET_KEY' zaroor set karein
app.secret_key = os.environ.get("SECRET_KEY", "bhai_ka_shop_2026_universal")

# Featured Products (Jo homepage par hamesha dikhenge)
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
        "description": "Powerful multitasking with S-Pen support.",
        "amazon_link": "https://www.amazon.in/s?k=samsung+s23+ultra",
        "flipkart_link": "https://www.flipkart.com/search?q=samsung+s23+ultra"
    }
]

@app.route('/')
def index():
    # User ne jo search kiya wo query yahan aayegi
    query = request.args.get('query', '').strip()
    
    if query:
        # 1. Pehle featured list mein check karo
        results = [p for p in featured_products if query.lower() in p['name'].lower()]
        
        # 2. AGAR LIST MEIN NAHI MILA -> Toh on-the-spot naya product card banao
        if not results:
            # Ye card har us product ke liye banega jo list mein nahi hai
            dynamic_product = {
                "name": query.title(), # User ki query ka pehla letter capital karega
                "price": "Check Live Price",
                "image": "default.jpg", # Placeholder image
                "description": f"Find the best deals for '{query}' on India's top stores.",
                # Space ko '+' se replace kiya taaki URL sahi se kaam kare
                "amazon_link": f"https://www.amazon.in/s?k={query.replace(' ', '+')}",
                "flipkart_link": f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
            }
            results = [dynamic_product]
    else:
        results = featured_products

    return render_template("index.html", products=results, query=query)

# --- Auth Routes (Same as before) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = "Admin"
        return redirect(url_for('index'))
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- Render Production Port Binding ---
if __name__ == "__main__":
    # Render dynamic port environment variable
    port = int(os.environ.get("PORT", 10000))
    # host 0.0.0.0 is mandatory for cloud deployment
    app.run(host="0.0.0.0", port=port, debug=False)

