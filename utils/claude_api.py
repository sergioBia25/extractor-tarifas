import anthropic
import json
import os
from dotenv import load_dotenv
from config.config import CLAUDE_API_CONFIG, RETRY_CONFIG
import requests
import time

class ClaudeAPI:
    """Clase para manejar la comunicación con la API de Claude"""
    
    def __init__(self, api_key):
        """Inicializar con la API key de Claude"""
        self.client = anthropic.Anthropic(api_key=api_key)
        self.headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
    
    def procesar_texto(self, text, instructions):
        """Procesa el texto usando Claude y devuelve el resultado en formato CSV."""
        try:
            # Construir el prompt
            prompt = f"""{instructions}

A continuación está el texto extraído del documento de tarifas:

{text}

IMPORTANTE: Por favor, organiza los datos en formato CSV con las siguientes columnas en este orden exacto:
Comercializador,Mercado,Nivel de Tensión,G,T,D,C,COT,P,R,CU,CU + COT

REGLAS ESTRICTAS:
1. La primera línea DEBE ser exactamente: Comercializador,Mercado,Nivel de Tensión,G,T,D,C,COT,P,R,CU,CU + COT
2. Los valores numéricos deben usar punto como separador decimal
3. No usar separadores de miles
4. No incluir espacios extras entre columnas
5. No incluir texto adicional antes o después del CSV
6. Asegurarse de que todas las columnas estén presentes y en el orden correcto"""

            # Intentar con reintentos en caso de fallo
            for attempt in range(RETRY_CONFIG["max_retries"]):
                try:
                    print(f"Intento {attempt+1}/{RETRY_CONFIG['max_retries']}...")
                    
                    # Llamar a Claude
                    response = self.client.messages.create(
                        model=CLAUDE_API_CONFIG["model"],
                        max_tokens=CLAUDE_API_CONFIG["max_tokens"],
                        temperature=0,
                        system="Eres un asistente especializado en procesar documentos de tarifas eléctricas y convertirlos a formato CSV. Tu única tarea es extraer los datos y devolverlos en formato CSV, sin ningún texto adicional. Debes seguir estrictamente el formato de columnas especificado.",
                        messages=[
                            {"role": "user", "content": prompt}
                        ]
                    )
                    
                    # Extraer el contenido de la respuesta
                    content = response.content[0].text.strip()
                    
                    # Imprimir la respuesta para depuración
                    print("\nRespuesta de Claude:")
                    print("-" * 50)
                    print(content[:500] + "..." if len(content) > 500 else content)
                    print("-" * 50)
                    
                    # Verificar que la respuesta comienza con el encabezado correcto
                    expected_header = "Comercializador,Mercado,Nivel de Tensión,G,T,D,C,COT,P,R,CU,CU + COT"
                    
                    # Limpiar la respuesta de posibles espacios o caracteres especiales
                    content_lines = content.strip().split('\n')
                    if not content_lines:
                        print("La respuesta está vacía")
                        continue
                        
                    first_line = content_lines[0].strip()
                    print(f"\nPrimera línea de la respuesta: '{first_line}'")
                    print(f"Encabezado esperado: '{expected_header}'")
                    
                    if first_line != expected_header:
                        print("La respuesta no tiene el formato CSV esperado. Reintentando...")
                        if attempt < RETRY_CONFIG["max_retries"] - 1:
                            time.sleep(RETRY_CONFIG["retry_delay"] * (2 ** attempt))
                            continue
                        raise ValueError("La respuesta no tiene el formato CSV esperado")
                    
                    # Verificar que todas las líneas tienen el número correcto de columnas
                    expected_columns = len(expected_header.split(','))
                    for i, line in enumerate(content_lines[1:], 2):
                        columns = line.strip().split(',')
                        if len(columns) != expected_columns:
                            print(f"Error en línea {i}: número incorrecto de columnas")
                            if attempt < RETRY_CONFIG["max_retries"] - 1:
                                time.sleep(RETRY_CONFIG["retry_delay"] * (2 ** attempt))
                                continue
                            raise ValueError(f"Error en línea {i}: número incorrecto de columnas")
                    
                    # Si llegamos aquí, la respuesta es válida
                    return content
                    
                except Exception as e:
                    print(f"Error en el intento {attempt+1}: {str(e)}")
                    if attempt < RETRY_CONFIG["max_retries"] - 1:
                        wait_time = RETRY_CONFIG["retry_delay"] * (2 ** attempt)
                        print(f"Reintentando en {wait_time} segundos...")
                        time.sleep(wait_time)
                    else:
                        raise Exception(f"Error al procesar el texto con Claude después de {RETRY_CONFIG['max_retries']} intentos: {str(e)}")
            
        except Exception as e:
            raise Exception(f"Error al procesar el texto con Claude: {str(e)}")

    def procesar_texto_con_reintentos(self, texto, instrucciones, max_retries=None, retry_delay=None, initial_timeout=None):
        """Envía texto a Claude para su procesamiento con manejo de reintentos"""
        # Usar configuración por defecto si no se especifica
        max_retries = max_retries or RETRY_CONFIG["max_retries"]
        retry_delay = retry_delay or RETRY_CONFIG["retry_delay"]
        timeout = initial_timeout or RETRY_CONFIG["initial_timeout"]
        
        # Construir el prompt completo
        prompt = f"""{instrucciones}

A continuación está el texto extraído del documento de tarifas:

{texto}

IMPORTANTE: Por favor, organiza los datos en formato CSV con las siguientes columnas en este orden exacto:
Comercializador,Mercado,Nivel de Tensión,G,T,D,C,COT,P,R,CU,CU + COT

Asegúrate de que la respuesta sea SOLO el CSV, sin texto adicional antes o después."""
        
        # Preparar datos para la API
        message_data = {
            "model": CLAUDE_API_CONFIG["model"],
            "max_tokens": CLAUDE_API_CONFIG["max_tokens"],
            "temperature": 0,  # Temperatura 0 para respuestas más consistentes
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }
        
        # Intentar con reintentos en caso de fallo
        for attempt in range(max_retries):
            try:
                print(f"Intento {attempt+1}/{max_retries} (timeout: {timeout}s)...")
                response = requests.post(
                    CLAUDE_API_CONFIG["base_url"],
                    headers=self.headers,
                    json=message_data,
                    timeout=timeout
                )
                
                if response.status_code == 200:
                    csv_content = response.json()["content"][0]["text"].strip()
                    # Verificar que la respuesta comienza con el encabezado CSV
                    if not csv_content.startswith("Comercializador,Mercado,Nivel de Tensión"):
                        print("La respuesta no está en formato CSV. Reintentando...")
                        if attempt < max_retries - 1:
                            continue
                        return None
                    return csv_content
                
                elif response.status_code == 429:  # Rate limit
                    wait_time = retry_delay * (2 ** attempt)
                    print(f"Rate limit alcanzado. Esperando {wait_time} segundos...")
                    time.sleep(wait_time)
                    continue
                
                else:
                    print(f"Error en la API: {response.status_code}")
                    print(f"Detalles: {response.text}")
                    
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        print(f"Reintentando en {wait_time} segundos...")
                        time.sleep(wait_time)
                    else:
                        return None
            
            except requests.exceptions.Timeout:
                print(f"Timeout al comunicarse con la API (después de {timeout} segundos)")
                
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    timeout = min(timeout * 1.5, 600)  # Aumentar hasta máximo 10 minutos
                    print(f"Reintentando en {wait_time} segundos con timeout aumentado a {timeout}s...")
                    time.sleep(wait_time)
                else:
                    return None
                    
            except Exception as e:
                print(f"Error al comunicarse con la API: {e}")
                
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    print(f"Reintentando en {wait_time} segundos...")
                    time.sleep(wait_time)
                else:
                    return None
        
        return None 