from flask import Flask, request, jsonify
from pdfminer.high_level import extract_text as extract_pdf_text
from docx import Document
from tika import parser  # Import Tika
import os
from io import BytesIO

app = Flask(__name__)

# Maximum file size (5 MB)
MAX_FILE_SIZE = 5 * 1024 * 1024


def extract_text_from_pdf(pdf_file):
    """Extract text from PDFs using PDFMiner."""
    try:
        # Convert FileStorage object to bytes for PDFMiner
        file_content = pdf_file.read()
        text = extract_pdf_text(BytesIO(file_content))
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {e}")


def extract_text_from_docx(docx_file):
    """Extract text from Word (.docx) files."""
    try:
        doc = Document(docx_file)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error extracting text from DOCX: {e}")


def extract_text_from_doc(doc_file):
    """Extract text from Word (.doc) files using Tika."""
    try:
        # Save the file temporarily for Tika processing
        temp_filename = "temp.doc"
        with open(temp_filename, "wb") as f:
            f.write(doc_file.read())

        # Use Tika to parse the .doc file
        parsed = parser.from_file(temp_filename)
        os.remove(temp_filename)  # Clean up the temporary file

        if not parsed or not parsed.get("content"):
            raise ValueError("Tika failed to extract text from the document.")

        return parsed["content"].strip()
    except Exception as e:
        raise ValueError(f"Error extracting text from DOC: {e}")


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
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file)
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(file)
        elif filename.endswith('.doc'):
            text = extract_text_from_doc(file)
        else:
            return jsonify({"error": "Unsupported file type. Only .pdf, .docx, and .doc are supported."}), 400

        return jsonify({"text": text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
