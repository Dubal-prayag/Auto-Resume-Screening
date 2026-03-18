import pdfplumber
import docx
import io


def extract_text_from_pdf(file_bytes):
    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            # layout=True preserves 2-column spatial arrangement
            page_text = page.extract_text(layout=True)
            if page_text:
                text += page_text + " "
    return text.strip()


def extract_text_from_docx(file_bytes):
    doc = docx.Document(io.BytesIO(file_bytes))
    return " ".join([para.text for para in doc.paragraphs if para.text])


def extract_text(uploaded_file):
    file_bytes = uploaded_file.read()
    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)

    elif name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)

    else:
        return file_bytes.decode("utf-8", errors="ignore")