import fitz  # PyMuPDF
import os
import re

def extract_text_from_pdf(pdf_path, output_folder="outputs"):
    """
    Extrae solo títulos y párrafos de un paper en PDF y los guarda en Markdown.
    :param pdf_path: Ruta del archivo PDF.
    :param output_folder: Carpeta donde se guardará la salida en formato Markdown.
    """
    doc = fitz.open(pdf_path)
    paper_name = os.path.basename(pdf_path).replace(".pdf", "")
    markdown_output = os.path.join(output_folder, f"{paper_name}.md")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    md_content = []

    # 🔹 Extraer el título del paper
    first_page = doc[0]
    title_text = ""
    for block in first_page.get_text("blocks"):
        text = block[4].strip()
        if len(text) > 20 and len(text) < 150 and text.isupper():  # Títulos suelen estar en mayúsculas y son cortos
            title_text = text
            break

    md_content.append(f"# {title_text}\n") if title_text else md_content.append("# [Título No Detectado]\n")

    # 🔹 Procesar cada página asegurando el orden correcto de párrafos
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_width = page.rect.width
        page_height = page.rect.height

        # Dividir en dos columnas (izquierda y derecha)
        col_izquierda = fitz.Rect(0, 0, page_width / 2, page_height)
        col_derecha = fitz.Rect(page_width / 2, 0, page_width, page_height)

        text_izquierda = page.get_text("text", clip=col_izquierda).strip()
        text_derecha = page.get_text("text", clip=col_derecha).strip()

        # 🔹 Verificar el orden correcto de las columnas
        if len(text_izquierda) < len(text_derecha) * 0.5:
            text_izquierda, text_derecha = text_derecha, text_izquierda

        full_text = f"{text_izquierda}\n\n{text_derecha}"
        
        # 🔹 Limpiar y organizar la estructura
        structured_text = structure_text(full_text)

        md_content.append(f"### Página {page_num + 1}\n\n{structured_text}")

    # Guardar en un archivo Markdown
    with open(markdown_output, "w", encoding="utf-8") as f:
        f.write("\n\n".join(md_content))

    print(f"✅ Extracción completada. Archivo Markdown generado en: {markdown_output}")

def structure_text(text):
    """
    Organiza el texto en títulos y párrafos correctamente formateados.
    :param text: Texto extraído sin procesar.
    :return: Texto estructurado en Markdown.
    """
    lines = text.split("\n")
    cleaned_lines = []
    current_paragraph = ""

    for line in lines:
        line = line.strip()

        # Detectar títulos y subtítulos (mayúsculas o seguidos de ":")
        if len(line) < 80 and line.isupper():
            if current_paragraph:
                cleaned_lines.append(current_paragraph)
                current_paragraph = ""
            cleaned_lines.append(f"## {line}")

        elif len(line) < 100 and ":" in line:
            if current_paragraph:
                cleaned_lines.append(current_paragraph)
                current_paragraph = ""
            cleaned_lines.append(f"### {line}")

        else:
            # Si es parte de un párrafo, lo acumulamos
            if current_paragraph:
                current_paragraph += " " + line
            else:
                current_paragraph = line

    # Agregar el último párrafo
    if current_paragraph:
        cleaned_lines.append(current_paragraph)

    return "\n\n".join(cleaned_lines)

# 🔹 Prueba con un PDF
if __name__ == "__main__":
    pdf_path = "papers/aru.pdf"  # Cambia esto con tu PDF real
    extract_text_from_pdf(pdf_path)