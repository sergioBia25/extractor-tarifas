import os
import fitz
import pdfplumber
import numpy as np
from .image_processor import ImageProcessor
import cv2

class PDFProcessor:
    """Clase para procesar archivos PDF y extraer su contenido"""
    
    def __init__(self, image_processor=None):
        """Inicializar con un procesador de imágenes opcional"""
        self.image_processor = image_processor
    
    def extraer_texto_pdf(self, pdf_path):
        """Extrae el texto completo de un archivo PDF (texto + OCR de imágenes solo si es necesario)"""
        try:
            print(f"Extrayendo texto de {pdf_path}...")
            
            # Directorio donde se encuentra el PDF
            pdf_dir = os.path.dirname(pdf_path)
            file_name = os.path.splitext(os.path.basename(pdf_path))[0]
            text_output_path = os.path.join(pdf_dir, f"{file_name}_text.txt")
            
            # Extraer texto que puede ser seleccionado
            with pdfplumber.open(pdf_path) as pdf:
                # Inicializar texto vacío
                full_text = ""
                
                # Extraer texto de cada página
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n\n"
                    print(f"  Página {i+1}/{len(pdf.pages)} procesada (texto)")
            
            # Solo aplicar OCR si:
            # 1. No hay texto extraído (longitud < 100 caracteres)
            # 2. El procesador de imágenes está disponible
            if len(full_text.strip()) < 100 and self.image_processor:
                print("Detectado PDF con poco texto seleccionable. Aplicando OCR a las imágenes...")
                imagen_text = self.extraer_imagenes_pdf(pdf_path)
                if imagen_text:
                    full_text += "\n\n--- INICIO DE TEXTO EXTRAÍDO POR OCR ---\n\n"
                    full_text += imagen_text
                    full_text += "\n\n--- FIN DE TEXTO EXTRAÍDO POR OCR ---\n\n"
            
            # Verificación especial para Ruitoque
            if "Ruitoque" in full_text or "RUITOQUE" in full_text:
                print("\n¡ALERTA! Se ha detectado 'Ruitoque' en el texto.")
                print("Asegúrate de que los datos de Ruitoque se procesen correctamente.\n")
            
            # Guardar el texto en un archivo
            with open(text_output_path, "w", encoding="utf-8") as f:
                f.write(full_text)
            
            print(f"Texto extraído y guardado en '{text_output_path}'")
            return full_text, text_output_path
                
        except Exception as e:
            print(f"Error al extraer texto del PDF: {e}")
            return None, None
    
    def extraer_imagenes_pdf(self, pdf_path):
        """Extrae imágenes del PDF y aplica OCR para obtener texto"""
        try:
            if not self.image_processor:
                print("No se puede aplicar OCR: procesador de imágenes no disponible")
                return ""
                
            print(f"Extrayendo imágenes y aplicando OCR a {pdf_path}...")
            
            # Abrir el PDF con PyMuPDF
            pdf_document = fitz.open(pdf_path)
            num_paginas = len(pdf_document)
            
            all_text = []
            img_count = 0
            
            for page_num in range(num_paginas):
                print(f"Procesando página {page_num+1}/{num_paginas} para imágenes...")
                
                # Obtener la página actual
                page = pdf_document[page_num]
                
                # Obtener lista de imágenes en la página
                image_list = page.get_images(full=True)
                
                # Si no hay imágenes en esta página, continuar con la siguiente
                if not image_list:
                    continue
                
                for img_index, img_info in enumerate(image_list):
                    img_count += 1
                    xref = img_info[0]  # Número de referencia de la imagen
                    
                    # Extraer imagen
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Convertir bytes a formato numpy para OpenCV
                    nparr = np.frombuffer(image_bytes, np.uint8)
                    imagen = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                    
                    # Solo procesar imágenes lo suficientemente grandes
                    if imagen.shape[0] > 100 and imagen.shape[1] > 100:
                        print(f"  Extrayendo texto de imagen {img_count} (página {page_num+1})...")
                        
                        # Extraer texto de la imagen
                        texto_imagen = self.image_processor.extraer_texto_de_imagen(imagen)
                        
                        if texto_imagen.strip():
                            all_text.append(f"\n--- TEXTO DE IMAGEN (Página {page_num+1}, Imagen {img_index+1}) ---\n")
                            all_text.append(texto_imagen)
                            all_text.append("\n--- FIN TEXTO DE IMAGEN ---\n")
            
            pdf_document.close()
            return "\n".join(all_text)
            
        except Exception as e:
            print(f"Error al extraer imágenes del PDF: {e}")
            return "" 