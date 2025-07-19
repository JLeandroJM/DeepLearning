import os
from extract_text import extract_text_from_pdf
from extract_tables import extract_tables_from_pdf
from extract_equations import extract_equations_from_pdf
from extract_images import extract_images_and_text
from translate import translate_text
from save_markdown import save_as_markdown

# 📌 Ruta del PDF (ajusta según tu archivo)
pdf_file = "papers/primero.pdf"

# 📌 Crear una carpeta específica para el output basado en el nombre del PDF
pdf_name = os.path.splitext(os.path.basename(pdf_file))[0]
output_folder = f"outputs/{pdf_name}"
os.makedirs(output_folder, exist_ok=True)

# 📌 Extraer solo la PRIMERA PÁGINA
texto = extract_text_from_pdf(pdf_file, pages=[1])  
# Modifica para extraer solo la primera página
print(texto)
tablas = extract_tables_from_pdf(pdf_file, pages=[1])
ecuaciones = extract_equations_from_pdf(pdf_file, pages=[1])
imagenes = extract_images_and_text(pdf_file, output_folder, pages=[1])

# 📌 No traducir por ahora, solo ver qué extraemos
# texto_traducido = translate_text(texto)  

# 📌 Guardar en Markdown
output_md = f"{output_folder}/page_1.md"
contenido_md = f"# Página 1 del Paper\n\n## Texto extraído\n\n{texto}\n\n## Tablas\n\n{tablas}\n\n## Ecuaciones\n\n{ecuaciones}\n\n## Imágenes guardadas en {output_folder}"
save_as_markdown(contenido_md, output_md)

print(f"Markdown generado en {output_md}")