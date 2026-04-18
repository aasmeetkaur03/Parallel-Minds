"""
extractor.py
------------
PURPOSE : Reads uploaded PDF or DOCX files and returns plain text.
USED BY : app.py (called when user uploads a file)
DEPENDS ON : pdfplumber (for PDF), python-docx (for DOCX)

HOW IT WORKS:
  1. Receive the uploaded file from Streamlit
  2. Check the file extension (.pdf or .docx)
  3. Extract all text from it
  4. Return the text as a plain string
"""

import pdfplumber      # reads PDF files
import docx            # reads DOCX (Word) files
import io              # converts file bytes to readable stream


def extract_from_pdf(file_bytes):
    """
    Extract text from a PDF file.

    PARAMETERS:
        file_bytes : raw bytes of the uploaded PDF

    RETURNS:
        str : all text found in the PDF, page by page

    HOW TO TEST (Person 2):
        Open any PDF, read it with this function, print the result.
        If it prints readable text, it works.
    """
    text = ""

    # Open the PDF from memory (not from disk)
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:                        # some pages may be blank
                text += page_text + "\n"

    return text.strip()                          # remove extra whitespace


def extract_from_docx(file_bytes):
    """
    Extract text from a DOCX (Word) file.

    PARAMETERS:
        file_bytes : raw bytes of the uploaded DOCX

    RETURNS:
        str : all paragraphs joined into one string

    HOW TO TEST (Person 2):
        Open any Word document, read it with this function, print the result.
    """
    doc = docx.Document(io.BytesIO(file_bytes))

    # Each paragraph is one logical block of text in a Word doc
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]

    return "\n".join(paragraphs)


def extract_text(uploaded_file):
    """
    MAIN FUNCTION — called by app.py.

    Decides which extractor to use based on file type.

    PARAMETERS:
        uploaded_file : Streamlit file uploader object

    RETURNS:
        str  : extracted text if successful
        None : if file type is not supported
    """
    file_bytes = uploaded_file.read()            # read raw bytes
    filename   = uploaded_file.name.lower()      # get file name in lowercase

    if filename.endswith(".pdf"):
        return extract_from_pdf(file_bytes)

    elif filename.endswith(".docx"):
        return extract_from_docx(file_bytes)

    else:
        # Unsupported type — app.py will show text paste box instead
        return None
