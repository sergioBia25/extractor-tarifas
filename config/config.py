import os
from pathlib import Path

# Obtener la ruta del directorio raíz del proyecto
ROOT_DIR = str(Path(__file__).parent.parent)

# Ruta al archivo .env
ENV_FILE_PATH = os.path.join(ROOT_DIR, "private", ".env")

def get_tesseract_path():
    """Obtiene la ruta a Tesseract OCR según el sistema operativo"""
    if os.name == 'nt':  # Windows
        return r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    else:  # Linux, MacOS
        return "/usr/bin/tesseract"

# Configuración de la API de Claude
CLAUDE_API_CONFIG = {
    "model": "claude-sonnet-4-20250514",
    "max_tokens": 17000,
    "base_url": "https://api.anthropic.com/v1/messages"
}

# Configuración de reintentos
RETRY_CONFIG = {
    "max_retries": 3,
    "retry_delay": 2,
    "initial_timeout": 30
} 