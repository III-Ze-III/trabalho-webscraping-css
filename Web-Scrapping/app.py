import re
from decimal import Decimal, InvalidOperation
import re
from decimal import Decimal, InvalidOperation
from urllib.parse import urljoin

from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup

def parse_numeric_value(value):
    if not value:
        return None

    match = re.search(r'[-+]?\d[\d,]*(?:\.\d+)?', value)
    if not match:
        return None

    try:
        number = Decimal(match.group().replace(',', ''))
    except InvalidOperation:
        return None

    return number if number.is_finite() else None


categories = [ "Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Toys",
              "Beauty", "Automotive", "Health", "Food & Beverage", "Jewelry", "Office Supplies", 
              "Pet Supplies", "Music", "Art"]

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', categories=categories)

@app.route('/scrape', methods=['POST'])
def scrape():
    selected_category = request.form['category']

    url = 'https://scrapingsandbox.com'

    # Coleta os dados da página
    response = requests.get(url)

    # Analisa o conteúdo HTML da página usando BeautifulSoup
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        products = []
        for card in soup.find_all('a', class_='product-card'):
            category_element = card.find(class_='category')
            product_category = category_element.get_text(" ", strip=True) if category_element else None
            if not product_category or selected_category.casefold() != product_category.casefold():
                continue

            name_element = card.find(class_='product-name')
            price_element = card.find(class_='price')
            rating_element = card.find(class_='rating')
            product_url = card.get('href')

            product = {
                'name': name_element.get_text(" ", strip=True) if name_element else None,
                'price': price_element.get_text(strip=True) if price_element else None,
                'category': product_category,
                'rating': rating_element.get_text(" ", strip=True) if rating_element else None,
                'url': urljoin(url, product_url) if product_url else None,
            }
            product['price_value'] = parse_numeric_value(product['price'])
            product['rating_value'] = parse_numeric_value(product['rating'])
            products.append(product)

        priced_products = [product for product in products if product['price_value'] is not None]
        rated_products = [product for product in products if product['rating_value'] is not None]
        stats = {
            'count': len(products),
            'lowest_price': min(priced_products, key=lambda product: product['price_value']) if priced_products else None,
            'highest_price': max(priced_products, key=lambda product: product['price_value']) if priced_products else None,
            'average_price': (
                f"${sum((product['price_value'] for product in priced_products), Decimal('0')) / len(priced_products):.2f}"
                if priced_products else None
            ),
            'best_rated': max(rated_products, key=lambda product: product['rating_value']) if rated_products else None,
        }

        return render_template(
            'result.html',
            selected_category=selected_category,
            products=products,
            stats=stats,
        )
    else:
        return f"Failed to retrieve data from {url}. Status code: {response.status_code}"

if __name__ == '__main__':
    app.run(debug=True)