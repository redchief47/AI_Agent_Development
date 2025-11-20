import openai
import json

openai.api_key = "229f7c1abefb4027949356b5ca30ebb1.yEUyokb-5CzUUeB36nkmNoKY"

def extract_sections(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts sections from legal documents."},
                {"role": "user", "content": f"Extract the following sections from the Universal Credit Act 2025 text: definitions, obligations, responsibilities, eligibility, payments, penalties, record_keeping. Return as JSON object with keys: definitions, obligations, responsibilities, eligibility, payments, penalties, record_keeping. Text: {text[:4000]}"}
            ],
            max_tokens=1000
        )
        content = response.choices[0].message.content
        try:
            return json.loads(content)
        except:
            return {
                "definitions": content,
                "obligations": "Error extracting",
                "responsibilities": "Error extracting",
                "eligibility": "Error extracting",
                "payments": "Error extracting",
                "penalties": "Error extracting",
                "record_keeping": "Error extracting"
            }
    except Exception as e:
        return {
            "definitions": f"Error extracting: {str(e)}",
            "obligations": "Error extracting",
            "responsibilities": "Error extracting",
            "eligibility": "Error extracting",
            "payments": "Error extracting",
            "penalties": "Error extracting",
            "record_keeping": "Error extracting"
        }

if __name__ == "__main__":
    with open('extracted_text.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    sections = extract_sections(text)
    with open('sections.json', 'w', encoding='utf-8') as f:
        json.dump(sections, f, indent=4)
    print("Sections extracted and saved to sections.json")
