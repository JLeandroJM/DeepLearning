def save_as_markdown(text, output_file):
    """
    Guarda el texto en formato Markdown.
    """
    with open(output_file, "w") as f:
        f.write(text)

# Prueba
if __name__ == "__main__":
    texto_md = "# Título del Paper\n\nEste es un ejemplo de texto en Markdown."
    save_as_markdown(texto_md, "outputs/sample_paper.md")