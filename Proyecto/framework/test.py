import subprocess

def translate_text(text):
    """
    Traduce texto usando Llama.cpp en local, replicando el comando que funciona en la terminal.
    """
    model_path = "/Users/jleandrojm/llama_models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
    
    command = [
        "/opt/homebrew/bin/llama-run",
        model_path,
        f"Translate the following text from English to Spanish, preserving technical terms: {text}"
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("Error ejecutando la traducción:", e)
        print("Salida estándar:", e.stdout)
        print("Error estándar:", e.stderr)
        return None

# 🔹 Prueba con un texto de ejemplo
if __name__ == "__main__":
    english_text = """Introduction Large language models have made 
    remarkable strides in improving performance across 
    different domains with notable examples such as GPT 
    [Achiam et al., 2023], Gemini [Team et al., 2023], 
    and Claude [Anthropic, 2023]. Significant efforts have 
    been directed toward increasing model size and training 
    data to boost capabilities. However, scaling at training time 
    comes with steep costs, while scaling computation during inference 
    remains largely underexplored. """

    print("Texto en inglés:")
    print(english_text)

    translated_text = translate_text(english_text)

    print("\nTexto traducido:")
    print(translated_text if translated_text else "❌ Error en la traducción")