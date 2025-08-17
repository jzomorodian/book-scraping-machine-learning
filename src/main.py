from src.service.scraper import BookScraper
from src.core.ArgParser import ArgPars

if __name__ == "__main__":

    arg_parser = ArgPars()
    args = arg_parser.parse()
    category = args.category
    print(f"Scraping category: {category}")

    print(args.csv)

    # Initialize the BookScraper
    bs = BookScraper()

    # Call the method to get all books in the specified category
    books = bs.get_all_books(category)
    # Save the books to the specified output file

    # Print the number of books found
    print(f'{len(books)} books found in category {category}')

    if args.dlimages:
        print("Downloading book images...")
        bs.download_books_images(books)

    if args.csv:
        print("Saving data to CSV...")
        bs.save_books_to_csv(books, category)

    if args.excel:
        print("Saving data to Excel...")
        bs.save_books_to_excel(books, category)
