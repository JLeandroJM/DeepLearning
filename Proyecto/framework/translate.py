import subprocess

def translate_text(text):
    print(text)
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

