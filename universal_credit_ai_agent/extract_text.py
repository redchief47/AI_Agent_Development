import PyPDF2

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

if __name__ == "__main__":
    pdf_path = r"C:\Users\vinch\Downloads\ukpga_20250022_en.pdf"
    text = extract_text_from_pdf(pdf_path)
    with open('extracted_text.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    print("Text extracted and saved to extracted_text.txt")
