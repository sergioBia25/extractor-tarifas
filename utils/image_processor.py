import cv2
import numpy as np
import pytesseract
from PIL import Image

class ImageProcessor:
    """Clase para el procesamiento de imágenes y OCR"""
    
    def __init__(self, tesseract_path=None):
        """Inicializar con la ruta a Tesseract"""
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def mejorar_imagen_para_ocr(self, imagen):
        """Mejora la imagen para OCR aplicando preprocesamiento"""
        # Convertir a escala de grises si no lo está
        if len(imagen.shape) == 3:
            gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
        else:
            gris = imagen.copy()
        
        # Aplicar binarización adaptativa para mejorar el contraste
        binario = cv2.adaptiveThreshold(
            gris, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Reducción de ruido
        kernel = np.ones((1, 1), np.uint8)
        binario = cv2.morphologyEx(binario, cv2.MORPH_CLOSE, kernel)
        
        return binario
    
    def extraer_texto_de_imagen(self, imagen, config='--oem 3 --psm 6'):
        """Extrae texto de una imagen usando Tesseract OCR"""
        try:
            # Preprocesar la imagen para mejorar OCR
            imagen_mejorada = self.mejorar_imagen_para_ocr(imagen)
            
            # Extraer texto con Tesseract
            texto = pytesseract.image_to_string(
                imagen_mejorada, 
                lang='spa', 
                config=config
            )
            return texto
            
        except Exception as e:
            print(f"Error en OCR: {e}")
            return "ERROR EN OCR" 