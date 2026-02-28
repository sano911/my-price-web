import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request
import os

app = Flask(__name__)

def get_amazon_price(name):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.5"
        }
        url = f"https://www.amazon.in/s?k={name}"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        price = soup.find("span", {"class": "a-price-whole"}).text
        return f"₹{price}"
    except:
        return "Not Found"

def get_flipkart_price(name):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        url = f"https://www.flipkart.com/search?q={name}"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        price = soup.find("div", {"class": "_30jeq3"}).text
        return price
    except:
        return "Not Found"

@app.route('/', methods=['GET', 'POST'])
def index():
    amazon_price = None
    flipkart_price = None
    if request.method == 'POST':
        product = request.form.get('product')
        amazon_price = get_amazon_price(product)
        flipkart_price = get_flipkart_price(product)
    return render_template('index.html', amazon=amazon_price, flipkart=flipkart_price)

if __name__ == '__main__':
    # Render ke liye sahi port setting
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
