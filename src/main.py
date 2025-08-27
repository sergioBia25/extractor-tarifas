import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path de Python
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

from dotenv import load_dotenv
from src.tarifas_processor import TarifasElectricasProcessor
from config.config import ENV_FILE_PATH, get_tesseract_path
from config.comercializadores import COMERCIALIZADORES

def main():
    """Función principal para ejecutar el procesador"""
    try:
        # Cargar API key
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            # Intentar cargar desde .env
            if os.path.exists(ENV_FILE_PATH):
                load_dotenv(ENV_FILE_PATH)
                api_key = os.getenv("ANTHROPIC_API_KEY")
            else:
                print(f"Error: No se encontró el archivo .env en {ENV_FILE_PATH}")
                print("Por favor, asegúrate de que el archivo .env existe en la carpeta 'private' con el siguiente contenido:")
                print("ANTHROPIC_API_KEY=tu_api_key_aqui")
                return
            
            if not api_key:
                print("Error: No se encontró la API key de Anthropic en el archivo .env")
                print("Por favor, asegúrate de que el archivo .env contiene la línea:")
                print("ANTHROPIC_API_KEY=tu_api_key_aqui")
                return
        
        # Configurar Tesseract
        tesseract_path = get_tesseract_path()
        
        # Verificar si existe Tesseract
        if not os.path.exists(tesseract_path):
            print(f"ADVERTENCIA: No se encontró Tesseract OCR en {tesseract_path}")
            print("El procesamiento de tablas en imágenes no estará disponible.")
            print("Si necesitas procesar tablas en imágenes, instala Tesseract desde: https://github.com/UB-Mannheim/tesseract/wiki")
            tesseract_path = None
        
        # Inicializar el procesador
        procesador = TarifasElectricasProcessor(api_key)

        # Preguntar si desea procesar PDF o CSV
        print("\n¿Qué deseas procesar?")
        print("1. PDF")
        print("2. CSV")
        opcion = input("Selecciona una opción (1 o 2): ").strip()

        if opcion not in ["1", "2"]:
            print("Opción inválida. Saliendo.")
            return

        # Mostrar comercializadores disponibles
        print("\nComercializadores disponibles:")
        for i, (codigo, info) in enumerate(COMERCIALIZADORES.items(), 1):
            print(f"{i}. {info['name']}")

        # Solicitar selección del comercializador
        while True:
            try:
                seleccion = int(input("\nSeleccione el número del comercializador: "))
                if 1 <= seleccion <= len(COMERCIALIZADORES):
                    comercializador = list(COMERCIALIZADORES.keys())[seleccion - 1]
                    break
                else:
                    print("Por favor, seleccione un número válido.")
            except ValueError:
                print("Por favor, ingrese un número válido.")

        # Ruta común para PDF y CSV
        default_path = r"C:\Users\User\Desktop\Tarifas cursor\pdfs"

        # Lógica para CSV
        if opcion == "2":
            ruta_csv = input(f"Ingrese la ruta completa al archivo CSV (o presiona Enter para usar {default_path}): ").strip()

            if not ruta_csv:
                print(f"Usando directorio por defecto: {default_path}")
                os.makedirs(default_path, exist_ok=True)

                csv_files = [f for f in os.listdir(default_path) if f.lower().endswith('.csv')]
                if not csv_files:
                    print(f"No se encontraron archivos CSV en {default_path}")
                    return

                print("\nCSV disponibles:")
                for i, archivo in enumerate(csv_files, 1):
                    print(f"{i}. {archivo}")

                try:
                    seleccion_csv = int(input("\nSelecciona el número del archivo CSV a procesar: "))
                    if 1 <= seleccion_csv <= len(csv_files):
                        ruta_csv = os.path.join(default_path, csv_files[seleccion_csv - 1])
                    else:
                        print("Selección inválida.")
                        return
                except ValueError:
                    print("Entrada inválida.")
                    return

            if not os.path.exists(ruta_csv):
                print(f"Error: El archivo {ruta_csv} no existe.")
                return

            procesador.procesar_csv(ruta_csv, comercializador)
            print("\nProceso completado.")
            return

        # Lógica para PDF
        pdf_path = input(f"Ingresa la ruta completa al archivo PDF de tarifas (o presiona Enter para usar {default_path}):\n").strip()
        if not pdf_path:
            print(f"Usando directorio por defecto: {default_path}")
            os.makedirs(default_path, exist_ok=True)

            pdf_files = [f for f in os.listdir(default_path) if f.lower().endswith('.pdf')]
            if not pdf_files:
                print(f"No se encontraron archivos PDF en {default_path}")
                return

            print("\nPDFs disponibles:")
            for i, pdf in enumerate(pdf_files, 1):
                print(f"  {i}. {pdf}")

            try:
                selection = int(input("\nSelecciona el número del PDF a procesar: "))
                if 1 <= selection <= len(pdf_files):
                    pdf_path = os.path.join(default_path, pdf_files[selection - 1])
                else:
                    print("Selección inválida. Saliendo.")
                    return
            except ValueError:
                print("Entrada inválida. Saliendo.")
                return

        if not os.path.exists(pdf_path):
            print(f"Error: El archivo {pdf_path} no existe.")
            return

        csv_path, text_path = procesador.procesar_archivo(pdf_path, comercializador)

        if csv_path:
            print(f"\nArchivos generados:")
            print(f"  - CSV: {csv_path}")
            print(f"  - Texto: {text_path}")
            
            print(f"\n¿Deseas abrir el archivo CSV generado? (s/n)")
            if input().lower() == 's':
                try:
                    import subprocess
                    os.startfile(csv_path) if os.name == 'nt' else subprocess.call(['open', csv_path])
                except Exception as e:
                    print(f"No se pudo abrir el archivo: {e}")

        print("\nProceso completado.")

    except Exception as e:
        print(f"\nError inesperado: {str(e)}")
        print("Por favor, verifica que todos los archivos y configuraciones estén correctos.")
        return

if __name__ == "__main__":
    main()
