import argparse
import json
import os
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests

class ECourtsScraper:
    def __init__(self):
        self.driver = None
        self.base_url = "https://services.ecourts.gov.in/ecourtindia_v6/"

    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode for automation
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def close_driver(self):
        if self.driver:
            self.driver.quit()

    def search_case(self, cnr=None, case_type=None, case_number=None, case_year=None, state=None, court=None):
        self.driver.get(self.base_url)
        time.sleep(2)  # Wait for page load

        # Navigate to case status or search page (assuming it's the main page or a link)
        # Based on typical site structure, look for case search form
        try:
            # Select state if provided
            if state:
                state_select = Select(self.driver.find_element(By.ID, "sess_state_code"))  # Placeholder ID
                state_select.select_by_visible_text(state)

            # Select court if provided
            if court:
                court_select = Select(self.driver.find_element(By.ID, "court_code"))  # Placeholder ID
                court_select.select_by_visible_text(court)

            if cnr:
                # Input CNR
                cnr_input = self.driver.find_element(By.ID, "cino")  # Placeholder ID
                cnr_input.send_keys(cnr)
            else:
                # Input case details
                if case_type:
                    case_type_select = Select(self.driver.find_element(By.ID, "case_type"))  # Placeholder
                    case_type_select.select_by_visible_text(case_type)
                if case_number:
                    case_number_input = self.driver.find_element(By.ID, "case_no")  # Placeholder
                    case_number_input.send_keys(case_number)
                if case_year:
                    case_year_input = self.driver.find_element(By.ID, "case_year")  # Placeholder
                    case_year_input.send_keys(case_year)

            # Submit search
            submit_button = self.driver.find_element(By.ID, "search_btn")  # Placeholder
            submit_button.click()

            # Wait for results
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "case-details")))  # Placeholder

            # Parse results
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            case_info = self.parse_case_info(soup)
            return case_info
        except Exception as e:
            print(f"Error during search: {e}")
            return None

    def parse_case_info(self, soup):
        # Placeholder parsing logic
        # Extract serial number, court name, etc.
        case_data = {
            "serial_number": "N/A",
            "court_name": "N/A",
            "status": "Not found"
        }
        # Example: case_data["serial_number"] = soup.find("span", class_="serial").text if soup.find("span", class_="serial") else "N/A"
        return case_data

    def check_listing(self, date_type):
        # Navigate to cause list page
        self.driver.get(self.base_url + "causelist")  # Placeholder URL
        time.sleep(2)

        # Select date
        today = datetime.now()
        if date_type == 'tomorrow':
            target_date = today + timedelta(days=1)
        else:
            target_date = today

        date_str = target_date.strftime("%d/%m/%Y")

        # Input date and search
        date_input = self.driver.find_element(By.ID, "date")  # Placeholder
        date_input.send_keys(date_str)
        search_btn = self.driver.find_element(By.ID, "search_causelist")  # Placeholder
        search_btn.click()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "causelist-table")))  # Placeholder

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        listings = self.parse_listings(soup, date_str)
        return listings

    def parse_listings(self, soup, date_str):
        # Parse cause list for the date
        listings = []
        # Placeholder: find table rows and extract data
        return listings

    def download_pdf(self, url, filename):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"PDF downloaded: {filename}")
        except Exception as e:
            print(f"Error downloading PDF: {e}")

    def download_cause_list(self):
        # Navigate to cause list download page
        self.driver.get(self.base_url + "download_causelist")  # Placeholder
        time.sleep(2)

        # Assume there's a download link
        download_link = self.driver.find_element(By.LINK_TEXT, "Download Cause List PDF")  # Placeholder
        pdf_url = download_link.get_attribute("href")
        self.download_pdf(pdf_url, "cause_list.pdf")

    def save_results(self, data, filename):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Results saved to {filename}")

def main():
    parser = argparse.ArgumentParser(description="eCourts Scraper")
    parser.add_argument("--cnr", help="CNR number")
    parser.add_argument("--case-type", help="Case type")
    parser.add_argument("--case-number", help="Case number")
    parser.add_argument("--case-year", help="Case year")
    parser.add_argument("--state", help="State")
    parser.add_argument("--court", help="Court")
    parser.add_argument("--today", action="store_true", help="Check listings for today")
    parser.add_argument("--tomorrow", action="store_true", help="Check listings for tomorrow")
    parser.add_argument("--causelist", action="store_true", help="Download entire cause list")
    parser.add_argument("--output", default="results.json", help="Output file for results")
    args = parser.parse_args()

    scraper = ECourtsScraper()
    scraper.setup_driver()
    try:
        results = {}
        if args.cnr or (args.case_type and args.case_number and args.case_year):
            case_info = scraper.search_case(cnr=args.cnr, case_type=args.case_type, case_number=args.case_number, case_year=args.case_year, state=args.state, court=args.court)
            if case_info:
                print("Case Info:", case_info)
                results["case_info"] = case_info
                if args.today or args.tomorrow:
                    date_type = 'today' if args.today else 'tomorrow'
                    listings = scraper.check_listing(date_type)
                    print(f"Listings for {date_type}:", listings)
                    results["listings"] = listings
        if args.causelist:
            scraper.download_cause_list()
            results["cause_list_downloaded"] = True

        if results:
            scraper.save_results(results, args.output)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.close_driver()

if __name__ == "__main__":
    main()
