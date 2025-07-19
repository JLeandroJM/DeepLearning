import pdfplumber
import re

def extract_equations_from_pdf(pdf_path, pages=None):
    """
    Extrae ecuaciones en formato LaTeX de páginas específicas.
    :param pdf_path: Ruta del PDF.
    :param pages: Lista de páginas (Ej: [1, 2, 3]). Si es None, extrae todas.
    :return: Lista de ecuaciones encontradas.
    """
    equations = []
    with pdfplumber.open(pdf_path) as pdf:
        target_pages = pages if pages else range(1, len(pdf.pages) + 1)

        for i in target_pages:
            page = pdf.pages[i - 1]
            text = page.extract_text()
            if text:
                matches = re.findall(r"\$.*?\$", text)  # Busca ecuaciones en formato $...$
                equations.extend(matches)

    return equations