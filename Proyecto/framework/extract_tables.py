import camelot

def extract_tables_from_pdf(pdf_path, pages=None):
    """
    Extrae tablas de páginas específicas de un PDF.
    :param pdf_path: Ruta del PDF.
    :param pages: Lista de páginas (Ej: [1, 2, 3]). Si es None, extrae todas.
    :return: Tablas en formato Markdown.
    """
    if pages:
        pages_str = ",".join(map(str, pages))
    else:
        pages_str = "all"

    tables = camelot.read_pdf(pdf_path, pages=pages_str)
    markdown_tables = ""

    for i, table in enumerate(tables):
        markdown_tables += f"\n\n### Tabla {i+1}\n\n"
        markdown_tables += table.df.to_markdown(index=False)

    return markdown_tables.strip()