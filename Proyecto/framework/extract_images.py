from pdf2image import convert_from_path
import pytesseract
import os

def extract_images_and_text(pdf_path, output_folder="outputs/images", pages=None):
    """
    Extrae imágenes de páginas específicas de un PDF y usa OCR si es necesario.
    :param pdf_path: Ruta del PDF
    :param output_folder: Carpeta de salida
    :param pages: Lista de páginas a procesar (Ej: [1, 2, 3]). Si es None, extrae todas.
    :return: Lista de (ruta de imagen, texto extraído)
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    images = convert_from_path(pdf_path)
    extracted_text = []
    target_pages = pages if pages else range(1, len(images) + 1)

    for i in target_pages:
        img = images[i - 1]  # Índice base 0
        image_path = os.path.join(output_folder, f"page_{i}.png")
        img.save(image_path, "PNG")

        # Aplicar OCR a la imagen
        ocr_text = pytesseract.image_to_string(img)
        if ocr_text.strip():
            extracted_text.append((image_path, ocr_text.strip()))

    return extracted_text