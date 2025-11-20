import subprocess
import os

# Change to the script directory
os.chdir(os.path.dirname(__file__))

subprocess.run(['python', 'extract_text.py'])
subprocess.run(['python', 'summarize.py'])
subprocess.run(['python', 'extract_sections.py'])
subprocess.run(['python', 'check_rules.py'])

# Combine into final JSON
import json

with open('summary.txt', 'r', encoding='utf-8') as f:
    summary = f.read()

with open('sections.json', 'r', encoding='utf-8') as f:
    sections = json.load(f)

with open('rules.json', 'r', encoding='utf-8') as f:
    rules = json.load(f)

final = {
    "summary": summary,
    "sections": sections,
    "rules": rules
}

with open('final_report.json', 'w', encoding='utf-8') as f:
    json.dump(final, f, indent=4)

print("Final report saved to final_report.json")
