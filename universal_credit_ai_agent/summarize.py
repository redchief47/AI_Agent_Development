import requests
import json

def summarize_text(text):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.2",
        "prompt": f"Summarize the Universal Credit Act 2025 in 5-10 bullet points focusing on: Purpose, Key definitions, Eligibility, Obligations, Enforcement elements. Text: {text[:4000]}",  # Limit text for API
        "stream": False
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        result = response.json()
        return result['response']
    else:
        return "Error in summarization"

if __name__ == "__main__":
    with open('extracted_text.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    summary = summarize_text(text)
    with open('summary.txt', 'w', encoding='utf-8') as f:
        f.write(summary)
    print("Summary saved to summary.txt")
