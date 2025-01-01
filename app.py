from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup as bs
import re

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    try:
        # Get the search query from the form
        search_query = request.form.get('query')
        if not search_query:
            return render_template('error.html', message="Search query cannot be empty.")

        # Remove spaces from the search query
        sanitized_query = search_query.replace(" ", "")

        # Define headers for the request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        # Construct the Flipkart search URL
        flipkart_url = f"https://www.flipkart.com/search?q={sanitized_query}"
        response = requests.get(flipkart_url, headers=headers)

        # Check if the request was successful
        if response.status_code != 200:
            return render_template('error.html', message=f"Failed to fetch data from Flipkart. Status code: {response.status_code}")

        # Parse the HTML content
        soup = bs(response.text, "html.parser")

        # Extract product information
        product = soup.find_all("div", {"class": "cPHDOP col-12-12"})

        # Initialize lists for product details
        image_links = []
        product_names = []
        prices = []
        descriptions = []

        # Extract details for each product
        for item in product:
            try:
                img_tag = item.find('img')
                if img_tag and 'src' in img_tag.attrs:
                    image_links.append(img_tag['src'])

                if img_tag and 'alt' in img_tag.attrs:
                    product_names.append(img_tag['alt'])

                price = item.find('div', {'class': "Nx9bqj _4b5DiR"})
                if price:
                    prices.append(price.text)

                description = item.find('div', {'class': "_6NESgJ"})
                if description:
                    desc = description.text.replace('|', ',')
                    desc = re.sub(r'(\D)(\d)', r'\1 \2', desc)
                    desc = re.sub(r'(\d)(\D)', r'\1 \2', desc)
                    desc = re.sub(r'\s{2,}', ' ', desc).strip()
                    descriptions.append(desc)

            except Exception as e:
                # Log the error but continue processing other products
                print(f"Error processing item: {e}")

        # Check if any products were found
        if not product_names:
            return render_template('error.html', message="No products found for the given query.")

        # Combine the product details into a single list
        

        # Render the results page
        return render_template('results.html', products=products)

    except requests.exceptions.RequestException as e:
        # Handle request-specific errors
        return render_template('error.html', message=f"An error occurred while connecting to Flipkart: {e}")

    except Exception as e:
        # Handle general errors
        return render_template('error.html', message=f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    app.run(debug=True)
