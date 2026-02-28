from flask import Flask, render_template, request
import urllib.parse
import os

app = Flask(__name__)

# 👇 Apna Amazon affiliate tag yaha daalna
AMAZON_TAG = "yourtag-21"

def generate_amazon_link(product):
    query = urllib.parse.quote(product)
    return f"https://www.amazon.in/s?k={query}&tag={AMAZON_TAG}"

@app.route("/", methods=["GET", "POST"])
def index():
    amazon_link = None
    product = None

    if request.method == "POST":
        product = request.form.get("product")

        if product:
            amazon_link = generate_amazon_link(product)

    return render_template(
        "index.html",
        amazon_link=amazon_link,
        product=product
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
