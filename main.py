from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Scraping Logic
def get_prices(product_name):
    headers = {"User-Agent": "Mozilla/5.0"}
    results = {}
    
    # Amazon Logic
    try:
        amz_url = f"https://www.amazon.in/s?k={product_name}"
        res = requests.get(amz_url, headers=headers)
        soup = BeautifulSoup(res.content, 'html.parser')
        results['amazon'] = soup.find("span", {"class": "a-price-whole"}).text
    except:
        results['amazon'] = "Not Found"
        
    return results

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None
    if request.method == 'POST':
        p_name = request.form.get('p_name')
        data = get_prices(p_name)
    return render_template('index.html', prices=data)

if __name__ == "__main__":
    app.run(debug=True)
