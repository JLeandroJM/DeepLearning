import fitz  # PyMuPDF
import os
import re
import subprocess


def translate_text(text):
    """
    Traduce texto usando Llama.cpp en local, asegurando que sea limpio antes de la traducción.
    """
    model_path = "/Users/jleandrojm/llama_models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"

    
    text = clean_text(text)

    if not text.strip():
        return "[No se pudo traducir]"

    command = [
        "/opt/homebrew/bin/llama-run",
        model_path,
        f"Translate the following text from English to Spanish, preserving technical terms: {text}"
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("⚠️ Error ejecutando la traducción:", e)
        return "[Error en traducción]"


def clean_text(text):
    
    text = re.sub(r'\s+', ' ', text)  
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")  
    return text.strip()


def extract_text_from_pdf(pdf_path, output_folder="outputs"):
    
    doc = fitz.open(pdf_path)
    paper_name = os.path.basename(pdf_path).replace(".pdf", "")
    markdown_output = os.path.join(output_folder, f"{paper_name}.md")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    md_content = []

   
    first_page = doc[0]
    title_text = ""
    for block in first_page.get_text("blocks"):
        text = block[4].strip()
        if len(text) > 20 and len(text) < 150 and text.isupper():  
            title_text = text
            break

    title_translated = translate_text(title_text) if title_text else "[Título No Detectado]"
    md_content.append(f"# {title_translated}\n")

   
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_width = page.rect.width
        page_height = page.rect.height

       
        col_izquierda = fitz.Rect(0, 0, page_width / 2, page_height)
        col_derecha = fitz.Rect(page_width / 2, 0, page_width, page_height)

        text_izquierda = page.get_text("text", clip=col_izquierda).strip()
        text_derecha = page.get_text("text", clip=col_derecha).strip()

      
        if len(text_izquierda) < len(text_derecha) * 0.5:
            text_izquierda, text_derecha = text_derecha, text_izquierda

        full_text = f"{text_izquierda}\n\n{text_derecha}"

    
        structured_text = structure_and_translate(full_text)

        md_content.append(f"### Página {page_num + 1}\n\n{structured_text}")

    # Guardar en un archivo Markdown
    with open(markdown_output, "w", encoding="utf-8") as f:
        f.write("\n\n".join(md_content))

    print(f" Extracción y traducción completadas. Archivo Markdown generado en: {markdown_output}")


def structure_and_translate(text):
   
    lines = text.split("\n")
    cleaned_lines = []
    current_paragraph = ""

    for line in lines:
        line = line.strip()

        # Detectar títulos y subtítulos
        if len(line) < 80 and line.isupper():
            if current_paragraph:
                cleaned_lines.append(translate_text(current_paragraph))
                current_paragraph = ""
            cleaned_lines.append(f"## {translate_text(line)}")

        elif len(line) < 100 and ":" in line:
            if current_paragraph:
                cleaned_lines.append(translate_text(current_paragraph))
                current_paragraph = ""
            cleaned_lines.append(f"### {translate_text(line)}")

        else:
            
            if current_paragraph:
                current_paragraph += " " + line
            else:
                current_paragraph = line

    
    if current_paragraph:
        cleaned_lines.append(translate_text(current_paragraph))

    return "\n\n".join(cleaned_lines)


if __name__ == "__main__":
    pdf_path = "papers/aru.pdf"  # Cambia esto con tu PDF real
    extract_text_from_pdf(pdf_path)