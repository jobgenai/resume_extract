from flask import Flask, request, jsonify
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document
import subprocess
import os
import tempfile

app = Flask(__name__)

# Custom directory to avoid permission issues
TEMP_DIR = os.path.expanduser("~/my_temp_files")
os.makedirs(TEMP_DIR, exist_ok=True)

# Maximum file size (5 MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

LIBREOFFICE_PATH = "/Applications/LibreOffice.app/Contents/MacOS/soffice"


def convert_to_pdf(input_file, extension):
    """Convert DOC/DOCX to PDF using LibreOffice."""
    try:
        input_path = os.path.join(TEMP_DIR, f"input.{extension}")
        output_path = os.path.join(TEMP_DIR, "output.pdf")

        # Save the uploaded file
        with open(input_path, "wb") as f:
            f.write(input_file.read())

        # LibreOffice command to convert to PDF
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
    """Extract text from the converted PDF."""
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

    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > MAX_FILE_SIZE:
        return jsonify({"error": "File size exceeds the 5 MB limit."}), 400

    try:
        if filename.endswith('.docx'):
            pdf_path = convert_to_pdf(file, "docx")
        elif filename.endswith('.doc'):
            pdf_path = convert_to_pdf(file, "doc")
        else:
            return jsonify({"error": "Unsupported file type. Only .docx and .doc are supported."}), 400

        extracted_text = extract_text_from_pdf(pdf_path)

        # Cleanup temporary files
        os.remove(pdf_path)

        return jsonify({"text": extracted_text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
