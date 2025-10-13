# eCourts Scraper

A Python script to scrape court listings from the eCourts website (https://services.ecourts.gov.in/ecourtindia_v6/).

## Features

- Search for case details using CNR or case type, number, year.
- Check if a case is listed today or tomorrow.
- Display serial number and court name if listed.
- Optional PDF download for case details.
- Download entire cause list for today.
- Output to console and save as JSON/text files.
- CLI options for automation.

## Requirements

- Python 3.x
- Chrome browser (for Selenium)

## Installation

1. Clone or download the repository.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### CLI

Run the script with arguments:

```
python scraper.py --cnr <CNR> --today
python scraper.py --case-type <type> --case-number <number> --case-year <year> --state <state> --court <court> --tomorrow
python scraper.py --causelist
```

Options:
- `--cnr`: CNR number
- `--case-type`: Case type
- `--case-number`: Case number
- `--case-year`: Case year
- `--state`: State
- `--court`: Court
- `--today`: Check listings for today
- `--tomorrow`: Check listings for tomorrow
- `--causelist`: Download cause list
- `--output`: Output file (default: results.json)

### Example

```
python scraper.py --cnr 1234567890123 --today --output case_info.json
```

## Notes

- The script uses Selenium for browser automation due to the dynamic nature of the website.
- Element IDs and classes are placeholders and may need adjustment based on the actual site structure.
- Scraping government websites may have legal implications; use responsibly.
- For production, consider headless mode and proper error handling.

## Bonus: Web Interface

Run the web interface:

```
python web_interface.py
```

Then open http://127.0.0.1:5000/ in your browser for a simple web form to input details and scrape.
