import requests
import json
import csv
from datetime import datetime
import os
import time

def get_row_count(csv_file):
    """
    Returns the number of rows in the CSV file, excluding the header row.
    """
    row_count = 0
    try:
        with open(csv_file, 'r', encoding='utf-8') as csv_f:
            reader = csv.reader(csv_f)
            next(reader, None)  # Skip the header row
            row_count = sum(1 for row in reader)
    except FileNotFoundError:
        print(f"File {csv_file} not found. Starting with 0 rows.")
    except Exception as e:
        print(f"An error occurred while reading {csv_file}: {e}")
    return row_count+1

def write_member_data(data, csv_file):
    """
    Writes member data to CSV files.
    """

    with open(csv_file, 'a', newline='', encoding='utf-8') as csv_f:
        csv_writer = csv.writer(csv_f)
        terms = data.get('terms', {}).get('item', [])
        term_strings = []
        if terms:
            for term in terms:
                term_string = f"Start: {term.get('startYear', 'N/A')}, End: {term.get('endYear', 'N/A')}, Chamber: {term.get('chamber', 'N/A')}"
                term_strings.append(term_string)

            csv_writer.writerow([
                data.get('name', 'N/A'),
                data.get('bioguideId', 'N/A'),
                data.get('district', 'N/A'),
                data.get('partyName', 'N/A'),
                data.get('state', 'N/A'),
                "; ".join(term_strings)
            ])
        else:
            csv_writer.writerow([
                data.get('name', 'N/A'),
                data.get('bioguideId', 'N/A'),
                data.get('district', 'N/A'),
                data.get('partyName', 'N/A'),
                data.get('state', 'N/A'),
                'N/A'  # No terms found
            ])

def fetch_members(url, headers, requests_per_second):
    """
    Fetches member data from the API with rate limit handling.
    """
    response = None
    try:
        start_time = time.time()  # Record start time for rate limiting
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        members = data.get('members', [])

        for member in members:
            write_member_data(member, 'congress_members.csv')

        next_url = data.get('next')

        elapsed_time = time.time() - start_time
        if elapsed_time < (1 / requests_per_second):
            time.sleep((1 / requests_per_second) - elapsed_time)

        return next_url

    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        if response and response.status_code == 429:  # Check if the error is due to rate limiting
            print("Rate limit hit. Waiting 60 seconds")
            time.sleep(60)
            return url  # retry the current url
        return None
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return None
    except Exception as e:  # Catch other potential exceptions
        print(f"An unexpected error occurred: {e}")
        return None

def createCongressDataFile(base_url, API_KEY):
    csv_output_file = 'congress_members.csv'
    headers = {'X-Api-Key': API_KEY}
    requests_per_second = 1  # 1 request per second

    csv_file_exists = os.path.exists(csv_output_file)

    last_offset = get_row_count(csv_output_file)
    base_url = f"{base_url}?offset={last_offset}&limit=250"

    if not csv_file_exists:
        with open(csv_output_file, 'w', newline='', encoding='utf-8') as csv_f:
            csv_writer = csv.writer(csv_f)
            csv_writer.writerow(['Offset', 'Name', 'BioguideID', 'District', 'Party', 'State', 'Terms'])

    try:
        with open("last_url.txt", "r") as f:
            next_url = f.read().strip()
            print(f"Resuming from: {next_url}")
    except FileNotFoundError:
        next_url = base_url

    while next_url:
        next_url = fetch_members(next_url, headers, requests_per_second)
        if next_url:
            with open("last_url.txt", "w") as f:
                f.write(next_url)
        else:
            try:
                os.remove("last_url.txt")
            except FileNotFoundError:
                pass
    print(f"Member data written to: {csv_output_file}")