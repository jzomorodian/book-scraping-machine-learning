# Define the path to the argparser module
# This module is responsible for parsing command line arguments.
import argparse


class ArgPars:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="Book Scraper Argument Parser",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
        self.add_arguments()

    def add_arguments(self):
        self.parser.add_argument(
            '--category',
            '-c',
            type=str,
            required=False,
            default='Books',
            help='Category to scrape books from'
        )
        self.parser.add_argument(
            '--export',
            '-e',
            action="store_true",
            help="Export to excel and csv file"
        )
        self.parser.add_argument(
            '--dlimages',
            '-d',
            action='store_true',
            help='download images'
        )

    def parse(self):
        return self.parser.parse_args()
