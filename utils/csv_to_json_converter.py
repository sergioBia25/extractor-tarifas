import pandas as pd
import json
import os
from datetime import datetime
from config.example_json import MERCADOS, NIVELES_TENSION, OPERADORES

class CSVToJSONConverter:
    """Clase para convertir archivos CSV de tarifas a formato JSON"""
    
    def __init__(self):
        """Inicializar el convertidor"""
        self.mercados = MERCADOS
        self.niveles_tension = NIVELES_TENSION
        self.operadores = OPERADORES
    
    def _calcular_cot(self, cu_cot, comercializacion):
        """Calcula el valor correcto del COT"""
        if pd.isna(cu_cot) or pd.isna(comercializacion):
            return None
        return float(cu_cot) - float(comercializacion)
    
    def convertir_csv_a_json(self, csv_path):
        """
        Convierte un archivo CSV de tarifas eléctricas a formato JSON estructurado.
        
        Args:
            csv_path (str): Ruta al archivo CSV
            
        Returns:
            str: Ruta al archivo JSON generado
        """
        try:
            # Leer el CSV
            df = pd.read_csv(csv_path)
            
            # Verificar que las columnas requeridas existen
            required_columns = [
                'Comercializador', 'Mercado', 'Nivel de Tensión',
                'G', 'T', 'D', 'C', 'COT', 'P', 'R', 'CU', 'CU + COT'
            ]
            
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Columna requerida no encontrada: {col}")
            
            # Crear estructura base del JSON
            json_data = {
                "datos": []
            }
            
            # Procesar cada fila del CSV
            for _, row in df.iterrows():
                # Crear entrada de tarifa
                rate_entry = {
                    "Comercializador": str(row['Comercializador']),
                    "Mercado": str(row['Mercado']),
                    "Nivel de Tensión": str(row['Nivel de Tensión']),
                    "G": float(row['G']),
                    "T": float(row['T']),
                    "D": float(row['D']),
                    "C": float(row['C']),
                    "COT": float(row['COT']),
                    "P": float(row['P']),
                    "R": float(row['R']),
                    "CU": float(row['CU']),
                    "CU + COT": float(row['CU + COT'])
                }
                
                json_data["datos"].append(rate_entry)
            
            # Generar nombre del archivo JSON
            base_name = os.path.splitext(os.path.basename(csv_path))[0]
            json_path = os.path.join(os.path.dirname(csv_path), f"{base_name}.json")
            
            # Guardar el JSON
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            print(f"JSON guardado exitosamente en {json_path}")
            return json_path
            
        except Exception as e:
            print(f"Error al convertir CSV a JSON: {e}")
            return None 