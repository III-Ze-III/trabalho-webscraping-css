from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup

categories = [ "Eletronics", "Clothing", "Home & Garden", "Sports", "Books", "Toys", 
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

    # Lista para armazenar os dados coletados
    data = []

    # Analisa o conteúdo HTML da página usando BeautifulSoup
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Procura todos os cards de produtos na página
        category_spans = soup.find_all('a', class_='product-card')
        print(f"Found {len(category_spans)} product cards.")
    else:
        return f"Failed to retrieve data from {url}. Status code: {response.status_code}"
    
    return f"Scraping {selected_category}..."

if __name__ == '__main__':
    app.run(debug=True)