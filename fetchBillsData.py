import requests
import time
import csv
import os

# API Configuration
PAGE_SIZE = 50  # Number of results per page
MAX_RETRIES = 3  # Maximum retries for failed requests
RETRY_DELAY = 2  # Seconds to wait before retrying
CSV_FILE = "congressional_bills.csv"
BASE_URL = "https://api.congress.gov/v3"
API_KEY = os.environ.get("Congress_API_KEY")

def create_bill_data_file():
    """
    Fetch House and Senate bills from Congress.gov API with pagination and save to CSV.
    """
    params = {
        "billType": "hr,s",
        "pageSize": PAGE_SIZE,
        "api_key": API_KEY
    }

    offset = get_row_count(CSV_FILE)
    total_count = 0

    # Initialize CSV if not already set up
    initialize_csv()

    try:
        while True:
            params["offset"] = offset
            response = make_request(f"{BASE_URL}/bill", params)
            
            if response is None:
                print("Failed to retrieve data. Exiting.")
                break

            data = response.json()
            bills = data.get('bills', [])
            pagination = data.get('pagination', {})

            # Process and save each bill's data
            for bill in bills:
                total_count += 1
                bill_type = bill.get('type', 'UNKNOWN').lower()
                bill_number = bill.get('number', 'Unknown')
                congress = bill.get('congress', 'Unknown')

                # Fetch sponsor and co-sponsor details
                sponsor_data = fetch_bill_sponsor(congress, bill_type, bill_number)
                cosponsor_data = fetch_bill_cosponsors(congress, bill_type, bill_number)

                bill_data = {
                    "billType": bill_type.upper(),
                    "number": bill_number,
                    "title": bill.get('title', 'No Title'),
                    "sponsor": sponsor_data.get('name', 'Unknown'),
                    "sponsor_party": sponsor_data.get('party', 'Unknown'),
                    "sponsor_state": sponsor_data.get('state', 'Unknown'),
                    "coSponsors": "; ".join(cosponsor_data)
                }

                write_to_csv(bill_data)

            
                
            print(f"\nTotal Bills Found: {total_count}\n")

            offset = get_row_count(CSV_FILE)


    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")


def fetch_bill_sponsor(congress, bill_type, bill_number):
    """
    Fetch sponsor details for a specific bill.
    """
    url = f"{BASE_URL}/bill/{congress}/{bill_type}/{bill_number}"
    params = {"api_key": API_KEY}
    response = make_request(url, params)
    
    if response:
        data = response.json().get('bill', {})
        sponsor = data.get('sponsors', [{}])[0]
        return {
            "name": sponsor.get('fullName', 'Unknown Sponsor'),
            "party": sponsor.get('party', 'Unknown'),
            "state": sponsor.get('state', 'Unknown')
        }
    return {"name": "Unknown", "party": "Unknown", "state": "Unknown"}


def fetch_bill_cosponsors(congress, bill_type, bill_number):
    """
    Fetch co-sponsor details for a specific bill.
    """
    url = f"{BASE_URL}/bill/{congress}/{bill_type}/{bill_number}/cosponsors"
    params = {"api_key": API_KEY}
    response = make_request(url, params)
    
    cosponsor_list = []
    if response:
        cosponsors = response.json().get('cosponsors', [])
        for cosponsor in cosponsors:
            name = cosponsor.get('fullName', 'Unknown')
            party = cosponsor.get('party', 'Unknown')
            state = cosponsor.get('state', 'Unknown')
            cosponsor_list.append(f"{name} ({party} - {state})")
    return cosponsor_list


def make_request(url, params):
    """
    Handle API requests with retries and error handling.
    """
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response
            else:
                print(f"Error {response.status_code}: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
        
        print(f"Retrying ({attempt + 1}/{MAX_RETRIES}) in {RETRY_DELAY} seconds...")
        time.sleep(RETRY_DELAY)
    
    print("Max retries reached. Skipping this request.")
    return None


def initialize_csv():
    """
    Create a CSV file and write headers if it doesn't exist.
    """
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow([
                "Bill Type", "Number", "Title", "Sponsor", "Sponsor Party",
                "Sponsor State", "Co-Sponsors"
            ])
    print(f"CSV initialized: {CSV_FILE}")


def write_to_csv(bill_data):
    """
    Write a single bill's data to the CSV file.
    """
    with open(CSV_FILE, mode='a', newline='', encoding='utf-8') as csv_f:
        writer = csv.writer(csv_f)
        writer.writerow([
            bill_data["billType"],
            bill_data["number"],
            bill_data["title"],
            bill_data["sponsor"],
            bill_data["sponsor_party"],
            bill_data["sponsor_state"],
            bill_data["coSponsors"]
        ])
    print(f"Saved bill {bill_data['billType']} {bill_data['number']} to CSV.")


def get_row_count(csv_file):
    """
    Returns the number of rows in the CSV file.
    """
    try:
        with open(csv_file, 'r', encoding='utf-8') as csv_f:
            return sum(1 for row in csv.reader(csv_f)) - 1
    except FileNotFoundError:
        return 0
