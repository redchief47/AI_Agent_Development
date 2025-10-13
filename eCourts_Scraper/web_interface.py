from flask import Flask, request, jsonify, render_template_string
from scraper import ECourtsScraper
import json

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>eCourts Scraper</title>
</head>
<body>
    <h1>eCourts Scraper</h1>
    <form action="/scrape" method="post">
        <label>CNR: <input type="text" name="cnr"></label><br>
        <label>Case Type: <input type="text" name="case_type"></label><br>
        <label>Case Number: <input type="text" name="case_number"></label><br>
        <label>Case Year: <input type="text" name="case_year"></label><br>
        <label>State: <input type="text" name="state"></label><br>
        <label>Court: <input type="text" name="court"></label><br>
        <label><input type="checkbox" name="today"> Check Today</label><br>
        <label><input type="checkbox" name="tomorrow"> Check Tomorrow</label><br>
        <label><input type="checkbox" name="causelist"> Download Cause List</label><br>
        <input type="submit" value="Scrape">
    </form>
    {% if result %}
    <h2>Results:</h2>
    <pre>{{ result }}</pre>
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/scrape', methods=['POST'])
def scrape():
    cnr = request.form.get('cnr')
    case_type = request.form.get('case_type')
    case_number = request.form.get('case_number')
    case_year = request.form.get('case_year')
    state = request.form.get('state')
    court = request.form.get('court')
    today = 'today' in request.form
    tomorrow = 'tomorrow' in request.form
    causelist = 'causelist' in request.form

    scraper = ECourtsScraper()
    scraper.setup_driver()
    try:
        results = {}
        if cnr or (case_type and case_number and case_year):
            case_info = scraper.search_case(cnr=cnr, case_type=case_type, case_number=case_number, case_year=case_year, state=state, court=court)
            if case_info:
                results["case_info"] = case_info
                if today or tomorrow:
                    date_type = 'today' if today else 'tomorrow'
                    listings = scraper.check_listing(date_type)
                    results["listings"] = listings
        if causelist:
            scraper.download_cause_list()
            results["cause_list_downloaded"] = True

        result_json = json.dumps(results, indent=4)
    except Exception as e:
        result_json = f"Error: {e}"
    finally:
        scraper.close_driver()

    return render_template_string(HTML_TEMPLATE, result=result_json)

if __name__ == '__main__':
    app.run(debug=True)
