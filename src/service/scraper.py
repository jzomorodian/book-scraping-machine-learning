import requests
from bs4 import BeautifulSoup as BfS
import time
import csv
import os
import json
import pandas as pd
# from tqdm import tqdm, trange


class BookScraper:
    def __init__(self,):
        self.base_url = 'http://books.toscrape.com/'

        # This will hold all categories fetched from the site
        # It will be a dictionary with category names as keys
        # and their URLs as values
        self.all_categories = {}

    def get_book_details(self, book_url):
        """
        Fetches and parses a single book's detail page to extract data.

        Args:
            book_url (str): The URL of the book's detail page.

        Returns:
            dict: A dictionary containing the book's details,
            or None if the page fails to load.
        """
        try:
            response = requests.get(book_url)
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {book_url}: {e}")
            return None

        # --- Data Extraction ---
        soup = BfS(response.content, 'html.parser')
        title = soup.find('div', class_='product_main').find('h1').text
        price = soup.find('p', class_='price_color').text

        # The rating is stored in the class name (e.g., "star-rating Four")
        rating_tag = soup.find('p', class_='star-rating')
        # Get the second class, which is the rating
        rating = rating_tag['class'][1] if rating_tag else 'N/A'

        # Product information is in a table
        table = soup.find('table', class_='table-striped')
        rows = table.find_all('tr')

        # Extract data from specific table rows
        upc = rows[0].find('td').text
        availability = rows[5].find('td').text.strip()
        description = soup.find('meta', attrs={'name': 'description'})[
            'content'].strip()
        price_excl_tax = rows[2].find('td').text.strip()
        price_incl_tax = rows[3].find('td').text.strip()
        tax = rows[4].find('td').text.strip()
        number_of_reviews = rows[6].find('td').text.strip()
        image_url = soup.find('img')['src']

        return {
            'title': title,
            'price': price,
            'rating': rating,
            'availability': availability,
            'description': description,
            'upc': upc,
            'price_excl_tax': price_excl_tax,
            'price_incl_tax': price_incl_tax,
            'tax': tax,
            'number_of_reviews': number_of_reviews,
            'url': book_url,
            'image_url': requests.compat.urljoin(self.base_url, image_url),
        }

    def get_all_categories(self) -> dict:
        """
        Fetches all categories from the main page of the book store.
        Returns:
            list: A list of dictionaries containing category names and
            their corresponding links.
        """
        try:
            # make a request to the base URL:
            response = requests.get(self.base_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {self.base_url}: {e}")
            return None

        # create a list for all links of the categories:
        dict_of_categories = {}
        soup = BfS(response.text, 'html.parser')
        # take information for the sidebar: categories
        categories = soup.select(".side_categories a")

        for category in categories:
            # create one link of each category:
            link = self.base_url + category["href"]
            # find the category name:
            category_name = category.text.strip()
            # print the category name:
            print(f"Category: {category_name}, Link: {link}")
            # append the link to the list:
            dict_of_categories[category_name] = link

        # Store the categories in the instance variable
        self.all_categories = dict_of_categories

        return dict_of_categories

    def get_all_books(self, category_name: str = 'Books'):
        """
        Fetches all books from a given category name.

        Args:
            category_name (str): The name of the category page.

        Returns:
            list: A list of dictionaries containing book details.
        """
        books = []
        if not self.all_categories:
            self.get_all_categories()

        if category_name in self.all_categories:
            current_url = self.all_categories[category_name]
            print(f"Fetching books from category: {category_name}")
        else:
            print(f"Category '{category_name}' not found.")
            return []
        # make a request to the category URL:

        while current_url:
            print(f"Scraping page: {current_url}")

            try:
                response = requests.get(current_url)
                response.raise_for_status()

                # Parse the response content
                soup = BfS(response.content, 'html.parser')

                # --- Find all book links on the current page ---
                book_pods = soup.find_all('article', class_='product_pod')
                for pod in book_pods:
                    book_relative_url = pod.find('h3').find('a')['href']
                    # Construct the absolute URL for the book
                    book_full_url = requests.compat.urljoin(
                        current_url, book_relative_url)
                    print(f"Found book: {book_full_url}")
                    # Get details for each book and add to our list
                    book_details = self.get_book_details(book_full_url)
                    if book_details:
                        books.append(book_details)

                    # Be a good web citizen and pause between requests
                    time.sleep(0.1)

                # --- Pagination ---
                # Check if there is a 'next' page link
                # --- Check for a 'next' page link to continue pagination ---
                next_button = soup.find('li', class_='next')
                if next_button:
                    next_page_relative_url = next_button.find('a')['href']
                    # Construct the absolute URL for the next page
                    current_url = requests.compat.urljoin(
                        current_url, next_page_relative_url)
                else:
                    # If no 'next' button, we've reached the last page
                    current_url = None

            except requests.exceptions.RequestException as e:
                print(f"Error on page {current_url}: {e}")
                current_url = None  # Stop if a page fails

        self.save_books_to_json(books, category_name)

        return books

    def save_books_to_json(self, books, category_name):
        """
        Saves the list of books to a JSON file.

        Args:
            books (list): List of book dictionaries.
            filename (str): The name of the file to save the books.
        """

        if books:
            output_filename = f'exports/{category_name}.json'
            print(f"Saving data to {output_filename}...")

            with open(output_filename, 'w', encoding='utf-8') as f:
                json.dump(books, f, ensure_ascii=False, indent=4)

            print("Data saved successfully.")

    def save_books_to_csv(self, books, category_name):
        """
        Saves the list of books to a CSV file.

        Args:
            books (list): List of book dictionaries.
            filename (str): The name of the file to save the books.
        """
        # --- Save the collected data to a CSV file ---
        if books:
            output_filename = f'exports/{category_name}.csv'
            print(f"Saving data to {output_filename}...")

            # Use the keys from the first dictionary as headers
            headers = books[0].keys()

            with open(output_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(books)

            print("Data saved successfully.")

    def save_books_to_excel(self, books, category_name):
        """
        Saves the list of books to an Excel file.

        Args:
            books (list): List of book dictionaries.
            filename (str): The name of the file to save the books.
        """

        if books:
            output_filename = f'exports/{category_name}.xlsx'
            print(f"Saving data to {output_filename}...")

            df = pd.DataFrame(books)
            df.to_excel(output_filename, index=False)

            print("Data saved successfully.")

    def download_books_images(self, books):
        """
        Downloads book images to a specified directory.

        Args:
            books (list): List of book dictionaries containing image URLs.
        """
        download_dir = 'images'
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)

        for book in books:
            image_url = book.get('image_url')
            if image_url:
                try:
                    response = requests.get(image_url)
                    response.raise_for_status()
                    # Extract the image filename from the URL
                    filename = os.path.join(
                        download_dir, image_url.split('/')[-1])
                    with open(filename, 'wb') as img_file:
                        img_file.write(response.content)
                    print(f"Downloaded {filename}")
                except requests.exceptions.RequestException as e:
                    print(f"Failed to download {image_url}: {e}")

    def load_books_from_json(self, category_name):
        """
        Loads books from a JSON file.

        Args:
            filename (str): The name of the JSON file to load.

        Returns:
            list: A list of book dictionaries.
        """
        filename = f'exports/{category_name}.json'
        if not os.path.exists(filename):
            print(f"File {filename} does not exist.")
            return []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                books = json.load(f)
            return books
        except FileNotFoundError:
            print(f"File {filename} not found.")
            return []
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {filename}: {e}")
            return []
