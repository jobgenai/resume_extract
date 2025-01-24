import subprocess
import os
from flask import Flask, request, jsonify
from pdfminer.high_level import extract_text as extract_pdf_text

app = Flask(__name__)

# Temporary directory
TEMP_DIR = "/tmp/resume_processing"
os.makedirs(TEMP_DIR, exist_ok=True)

LIBREOFFICE_PATH = "/usr/bin/libreoffice"  # Correct path for Render (Linux)

def convert_to_pdf(input_file, extension):
    """Convert DOC/DOCX to PDF using LibreOffice on Render"""
    try:
        input_path = os.path.join(TEMP_DIR, f"input.{extension}")
        output_path = os.path.join(TEMP_DIR, "output.pdf")

        with open(input_path, "wb") as f:
            f.write(input_file.read())

        # Command to convert document to PDF
        command = [
            LIBREOFFICE_PATH,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", TEMP_DIR,
            input_path
        ]

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if not os.path.exists(output_path):
            raise ValueError(f"Failed to convert document to PDF. Error: {result.stderr.strip()}")

        return output_path

    except Exception as e:
        raise ValueError(f"Error converting to PDF: {e}")

def extract_text_from_pdf(pdf_path):
    """Extract text from the converted PDF"""
    try:
        text = extract_pdf_text(pdf_path)
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {e}")

@app.route('/extract-text', methods=['POST'])
def extract_text():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filename = file.filename.lower()

    if filename.endswith('.docx'):
        pdf_path = convert_to_pdf(file, "docx")
    elif filename.endswith('.doc'):
        pdf_path = convert_to_pdf(file, "doc")
    else:
        return jsonify({"error": "Unsupported file type. Only .docx and .doc are supported."}), 400

    extracted_text = extract_text_from_pdf(pdf_path)

    os.remove(pdf_path)  # Cleanup the converted PDF

    return jsonify({"text": extracted_text}), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
