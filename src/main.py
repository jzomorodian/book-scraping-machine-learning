from src.service.scraper import BookScraper
from src.core.ArgParser import ArgPars

if __name__ == "__main__":

    arg_parser = ArgPars()
    args = arg_parser.parse()
    category = args.category
    print(f"Scraping category: {category}")

    # Initialize the BookScraper
    bs = BookScraper()

    # Call the method to get all books in the specified category
    books = bs.get_all_books(category)

    # Print the number of books found
    print(f'{len(books)} books found in category {category}')

    # If images are to be downloaded, call the download method
    if args.dlimages:
        print("Downloading book images...")
        bs.download_books_images(books)

    # Save the books to the specified output file
    if args.export:
        print("Exporting data")
        bs.export_books(books, category)
