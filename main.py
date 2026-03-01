import os
from flask import Flask, render_template, request, session, flash, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "universal_search_key_2026")

# Aapke fixed items (Featured Products)
products = [
    {
        "name": "iPhone 15 Pro Max",
        "price": "₹1,49,900",
        "image": "iphone15.jpg",
        "description": "Latest Apple iPhone.",
        "amazon_link": "https://www.amazon.in/s?k=iphone+15+pro+max",
        "flipkart_link": "https://www.flipkart.com/search?q=iphone+15+pro+max"
    }
]

@app.route('/')
def index():
    query = request.args.get('query', '').strip()
    
    if query:
        # 1. Pehle apni list mein dhoondo
        filtered_products = [p for p in products if query.lower() in p['name'].lower()]
        
        # 2. AGAR LIST MEIN NAHI MILA -> Toh on-the-spot naya product banao
        if not filtered_products:
            dynamic_product = {
                "name": query,
                "price": "Check Live Price",
                "image": "default.jpg", # Placeholder image
                "description": f"Search results for {query} on official stores.",
                # User ki query ko Amazon/Flipkart ke search URL mein fix kar diya
                "amazon_link": f"https://www.amazon.in/s?k={query.replace(' ', '+')}",
                "flipkart_link": f"https://www.flipkart.com/search?q={query.replace(' ', '+')}"
            }
            filtered_products = [dynamic_product]
    else:
        filtered_products = products

    return render_template("index.html", products=filtered_products, query=query)

# Baaki login/logout routes same rahenge...
@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template("login.html")

@app.route('/register')
def register():
    return render_template("register.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)

