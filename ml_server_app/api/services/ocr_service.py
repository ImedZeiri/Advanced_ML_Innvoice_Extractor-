import os
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re
import logging

logger = logging.getLogger(__name__)

class OCRService:
    """Service pour l'extraction de texte à partir d'images et de PDFs"""
    
    @staticmethod
    def preprocess_image(image):
        """Prétraitement de l'image pour améliorer la qualité de l'OCR"""
        # Conversion en niveaux de gris
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
        
        # Réduction du bruit
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # Binarisation adaptative
        binary = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        return binary
    
    @staticmethod
    def extract_text_from_image(image):
        """Extrait le texte d'une image en utilisant pytesseract"""
        try:
            # Prétraitement de l'image
            processed_image = OCRService.preprocess_image(image)
            
            # Extraction du texte avec pytesseract
            text = pytesseract.image_to_string(processed_image, lang='fra')
            
            return text
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du texte: {str(e)}")
            return ""
    
    @staticmethod
    def extract_text_from_pdf(pdf_path):
        """Convertit un PDF en images et extrait le texte de chaque page"""
        try:
            # Conversion du PDF en images
            images = convert_from_path(pdf_path)
            
            full_text = ""
            
            # Extraction du texte de chaque page
            for image in images:
                text = OCRService.extract_text_from_image(image)
                full_text += text + "\n\n"
            
            return full_text
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction du texte du PDF: {str(e)}")
            return ""
    
    @staticmethod
    def extract_invoice_number(text):
        """Extrait le numéro de facture du texte"""
        patterns = [
            r'(?:facture|invoice|n°|numéro)[\s:]*([A-Za-z0-9\-_/]{3,20})',
            r'(?:N°|No|Numéro)[\s:]?(?:facture|invoice)?[\s:]*([A-Za-z0-9\-_/]{3,20})',
            r'(?:facture|invoice)[\s:]?(?:N°|No|Numéro)?[\s:]*([A-Za-z0-9\-_/]{3,20})'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                return match.group(1).strip()
        
        return None
    
    @staticmethod
    def extract_date(text):
        """Extrait la date de facture du texte"""
        # Formats de date courants: JJ/MM/AAAA, JJ-MM-AAAA, etc.
        patterns = [
            r'(?:date|émission|émise le)[\s:]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'(\d{1,2}\s+(?:janvier|février|mars|avril|mai|juin|juillet|août|septembre|octobre|novembre|décembre)\s+\d{2,4})'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                return match.group(1).strip()
        
        return None
    
    @staticmethod
    def extract_amount(text):
        """Extrait le montant total de la facture"""
        patterns = [
            r'(?:total|montant|somme)[\s:]*(?:ttc|t\.t\.c\.)?[\s:]*(\d+[.,]\d{2})',
            r'(?:total|montant|somme)[\s:]*(?:ttc|t\.t\.c\.)?[\s:]*(\d+)',
            r'(?:ttc|t\.t\.c\.)[\s:]*(\d+[.,]\d{2})',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount = match.group(1).strip()
                # Normalisation du format (remplacement de la virgule par un point)
                amount = amount.replace(',', '.')
                return float(amount)
        
        return None
    
    @staticmethod
    def extract_tax_amount(text):
        """Extrait le montant de TVA de la facture"""
        patterns = [
            r'(?:tva|t\.v\.a\.|taxe)[\s:]*(\d+[.,]\d{2})',
            r'(?:tva|t\.v\.a\.|taxe)[\s:]*(\d+)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount = match.group(1).strip()
                # Normalisation du format (remplacement de la virgule par un point)
                amount = amount.replace(',', '.')
                return float(amount)
        
        return None
    
    @staticmethod
    def extract_supplier_name(text):
        """Extrait le nom du fournisseur"""
        # Cette fonction est simplifiée et nécessiterait une approche plus sophistiquée
        # pour une extraction précise du nom du fournisseur
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if i < 5 and len(line.strip()) > 3 and not re.search(r'facture|invoice', line, re.IGNORECASE):
                return line.strip()
        
        return None