import requests
import json

def check_rules(text, sections):
    rules = [
        {"rule": "Act must define key terms", "key": "definitions"},
        {"rule": "Act must specify eligibility criteria", "key": "eligibility"},
        {"rule": "Act must specify responsibilities of the administering authority", "key": "responsibilities"},
        {"rule": "Act must include enforcement or penalties", "key": "penalties"},
        {"rule": "Act must include payment calculation or entitlement structure", "key": "payments"},
        {"rule": "Act must include record-keeping or reporting requirements", "key": "record_keeping"}
    ]
    results = []
    for rule in rules:
        key = rule["key"]
        check = key in sections and sections[key] != "Error extracting"
        status = "pass" if check else "fail"
        evidence = f"Extracted {key}" if status == "pass" else "Not found"
        confidence = 90 if status == "pass" else 50
        results.append({
            "rule": rule["rule"],
            "status": status,
            "evidence": evidence,
            "confidence": confidence
        })
    return results

if __name__ == "__main__":
    with open('extracted_text.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    with open('sections.json', 'r', encoding='utf-8') as f:
        sections = json.load(f)
    rules = check_rules(text, sections)
    with open('rules.json', 'w', encoding='utf-8') as f:
        json.dump(rules, f, indent=4)
    print("Rules checked and saved to rules.json")
