import os
import sys
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv
import tempfile
import csv
import json
import tiktoken  # <-- Agregado para conteo preciso de tokens

# Agregar el directorio raíz al path de Python
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)

from config.config import get_tesseract_path, CLAUDE_API_CONFIG, RETRY_CONFIG
from utils.image_processor import ImageProcessor
from utils.pdf_processor import PDFProcessor
from utils.claude_api import ClaudeAPI
from utils.csv_to_json_converter import CSVToJSONConverter
from config.comercializadores import COMERCIALIZADORES

class TarifasElectricasProcessor:
    """
    Clase integrada para procesar tarifas eléctricas:
    1. Extrae el texto de PDFs de tarifas (con soporte para OCR en imágenes)
    2. Envía el texto o un CSV a Claude API con instrucciones específicas
    3. Obtiene y guarda el CSV estructurado
    """

    def __init__(self, api_key):
        if not api_key:
            raise ValueError("Se requiere una API key de Anthropic")

        self.api_key = api_key
        self.tesseract_path = get_tesseract_path()

        self.image_processor = ImageProcessor(self.tesseract_path)
        self.pdf_processor = PDFProcessor(self.image_processor)
        self.claude_api = ClaudeAPI(self.api_key)
        self.csv_to_json = CSVToJSONConverter()
        self.config = CLAUDE_API_CONFIG
        self.retry_config = RETRY_CONFIG

    def _contar_tokens_preciso(self, texto):
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(texto))

    def _cargar_instrucciones(self, comercializador):
        if comercializador not in COMERCIALIZADORES:
            raise ValueError(f"Comercializador no válido: {comercializador}")

        # Cargar instrucciones específicas del comercializador
        specific_path = os.path.join(root_dir, COMERCIALIZADORES[comercializador]["instrucciones_file"])
        if not os.path.exists(specific_path):
            raise ValueError(f"No se encontraron instrucciones para el comercializador {comercializador}")

        with open(specific_path, "r", encoding="utf-8") as f:
            return f.read()

    def visualizar_csv(self, csv_content):
        try:
            import io
            df = pd.read_csv(io.StringIO(csv_content))
            print("\nResumen del CSV generado:")
            print(f"  - Filas: {len(df)}")
            print(f"  - Mercados: {len(df['Mercado'].unique())}")
            print(f"  - Niveles de tensión: {len(df['Nivel de Tensión'].unique())}")
            print("\nPrimeras 5 filas:")
            print(df.head(5).to_string(index=False))
            return df
        except Exception as e:
            print(f"Error al visualizar el CSV: {e}")
            return None

    def guardar_csv(self, csv_content, output_path):
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(csv_content)
            print(f"CSV guardado exitosamente en {output_path}")
            return True
        except Exception as e:
            print(f"Error al guardar el CSV: {e}")
            return False

    def procesar_archivo(self, pdf_path, comercializador):
        try:
            texto, text_path = self.pdf_processor.extraer_texto_pdf(pdf_path)
            if not texto:
                print("No se pudo extraer texto del PDF")
                return None, None

            instrucciones = self._cargar_instrucciones(comercializador)

            # Calcular tokens de entrada (preciso)
            tokens_entrada = self._contar_tokens_preciso(texto) + self._contar_tokens_preciso(instrucciones)
            print(f"Tokens de entrada (preciso): {tokens_entrada}")

            print("\nProcesando el texto con Claude...")
            csv_content = self.claude_api.procesar_texto(texto, instrucciones)
            if not csv_content:
                print("No se pudo procesar el texto con Claude")
                return None, None

            # Calcular tokens de salida y total
            tokens_salida = self._contar_tokens_preciso(csv_content)
            print(f"Tokens de salida (preciso): {tokens_salida}")
            print(f"Tokens totales (entrada + salida): {tokens_entrada + tokens_salida}")

            output_dir = os.path.join(os.path.dirname(pdf_path), "output")
            os.makedirs(output_dir, exist_ok=True)

            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            csv_path = os.path.join(output_dir, f"{base_name}.csv")

            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write(csv_content)

            print("\u00a1Procesamiento completado exitosamente!")
            return csv_path, text_path

        except Exception as e:
            print(f"Error al procesar el archivo: {str(e)}")
            return None, None

    def procesar_csv(self, csv_path, comercializador):
        """Procesa un CSV como texto, enviándolo a Claude junto con instrucciones"""
        try:
            if not os.path.exists(csv_path):
                print(f"Archivo no encontrado: {csv_path}")
                return None

            # Leer el CSV y mostrar información sobre su contenido
            df = pd.read_csv(csv_path)
            print("\nInformación del CSV de entrada:")
            print(f"Columnas disponibles: {df.columns.tolist()}")
            if 'or_abbreviation' in df.columns:
                print(f"Mercados únicos en or_abbreviation: {sorted(df['or_abbreviation'].unique().tolist())}")
                print(f"Total de mercados únicos: {len(df['or_abbreviation'].unique())}")
            print(f"Total de filas: {len(df)}")

            with open(csv_path, "r", encoding="utf-8") as f:
                csv_text = f.read()

            instrucciones = self._cargar_instrucciones(comercializador)

            # Calcular tokens de entrada (preciso)
            tokens_entrada = self._contar_tokens_preciso(csv_text) + self._contar_tokens_preciso(instrucciones)
            print(f"Tokens de entrada (preciso): {tokens_entrada}")

            print("\nEnviando CSV como texto a Claude...")
            resultado = self.claude_api.procesar_texto(csv_text, instrucciones)

            if not resultado:
                print("No se obtuvo respuesta de Claude.")
                return None

            # Calcular tokens de salida y total
            tokens_salida = self._contar_tokens_preciso(resultado)
            print(f"Tokens de salida (preciso): {tokens_salida}")
            print(f"Tokens totales (entrada + salida): {tokens_entrada + tokens_salida}")

            # Crear directorio de salida si no existe
            output_dir = os.path.join(os.path.dirname(csv_path), "output")
            os.makedirs(output_dir, exist_ok=True)

            # Generar nombre del archivo de salida
            base_name = os.path.splitext(os.path.basename(csv_path))[0]
            output_path = os.path.join(output_dir, f"{base_name}_procesado.csv")

            # Guardar el resultado
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(resultado)

            # Leer el CSV de salida y mostrar información
            df_salida = pd.read_csv(output_path)
            print("\nInformación del CSV de salida:")
            print(f"Total de filas: {len(df_salida)}")
            print(f"Mercados únicos: {sorted(df_salida['Mercado'].unique().tolist())}")
            print(f"Total de mercados únicos: {len(df_salida['Mercado'].unique())}")
            print(f"Niveles de tensión únicos: {df_salida['Nivel de Tensión'].unique().tolist()}")

            print(f"\n\u2705 Archivo procesado guardado en: {output_path}")
            return output_path

        except Exception as e:
            print(f"\u274c Error al procesar el CSV con Claude: {e}")
            return None

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python tarifas_processor.py <ruta_archivo> <comercializador>")
        sys.exit(1)
        
    archivo = sys.argv[1]
    comercializador = sys.argv[2]
    
    # Cargar API key desde variables de entorno
    load_dotenv(os.path.join('private', '.env'))
    api_key = os.getenv('ANTHROPIC_API_KEY')
    
    if not api_key:
        print("Error: No se encontró la API key de Anthropic en las variables de entorno")
        sys.exit(1)
        
    processor = TarifasElectricasProcessor(api_key=api_key)
    
    if archivo.lower().endswith('.csv'):
        processor.procesar_csv(archivo, comercializador)
    else:
        processor.procesar_archivo(archivo, comercializador)
