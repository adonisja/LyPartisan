import requests
import json
import os
from fetchCongressData import createCongressDataFile
from fetchBillsData import create_bill_data_file
import csv
import shutil

def main():
    API_KEY = os.environ.get("Congress_API_KEY")
    
    if API_KEY is None:
        raise ValueError("API_KEY environment variable not set.")
    headers = {'X-Api-Key': API_KEY}

    choice = input('Menu:\n1 - Fetch Congressional Data\n2 - Fetch Bill Data\
        \n3 - Clean Your CSV File\nYour Choice: ')
    match choice:
        case '1':   
            try:
                base_url = 'https://api.congress.gov/v3/member'
                createCongressDataFile(base_url, API_KEY)
            except requests.exceptions.RequestException as e:
                print(f"Request Error: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")
        case '2':
            try:
                create_bill_data_file()
            except requests.exceptions.RequestException as e:
                print(f"Request Error: {e}")
            except Exception as e:
                print(f"An unexpected error occured: {e}")
        case default:
            print('Unknown Option chosen')

    # Remove the __pycache__ folder
    pycache_path = os.path.join(os.path.dirname(__file__), '__pycache__')
    if os.path.exists(pycache_path):
        shutil.rmtree(pycache_path)
        print(f"Removed __pycache__ folder at {pycache_path}")

if __name__ == '__main__':
    main()