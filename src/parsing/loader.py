from pypdf import PdfReader


def load_resume(pdf_path):
    """
    Reads a PDF resume and returns all its text.
    """

    reader = PdfReader(pdf_path)

    text = ""

    for page in reader.pages:
        text += page.extract_text() + "\n"

    return text