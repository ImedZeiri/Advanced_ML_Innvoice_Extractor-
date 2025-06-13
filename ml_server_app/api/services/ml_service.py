import os
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score
import pickle
import logging
import json
from django.conf import settings

logger = logging.getLogger(__name__)

class MLService:
    """Service pour l'extraction intelligente des données de facture avec ML"""
    
    MODEL_PATH = os.path.join(settings.BASE_DIR, 'api', 'ml_models')
    
    def __init__(self):
        """Initialise le service ML"""
        os.makedirs(self.MODEL_PATH, exist_ok=True)
        self.invoice_classifier = self._load_model('invoice_classifier.pkl')
    
    def _load_model(self, model_name):
        """Charge un modèle ML depuis le disque ou en crée un nouveau s'il n'existe pas"""
        model_path = os.path.join(self.MODEL_PATH, model_name)
        
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.error(f"Erreur lors du chargement du modèle {model_name}: {str(e)}")
        
        # Création d'un nouveau modèle par défaut
        return self._create_default_model()
    
    def _create_default_model(self):
        """Crée un modèle par défaut"""
        return Pipeline([
            ('vectorizer', TfidfVectorizer(max_features=5000)),
            ('classifier', RandomForestClassifier(n_estimators=100))
        ])
    
    def _save_model(self, model, model_name):
        """Sauvegarde un modèle ML sur le disque"""
        model_path = os.path.join(self.MODEL_PATH, model_name)
        
        try:
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            logger.info(f"Modèle {model_name} sauvegardé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde du modèle {model_name}: {str(e)}")
    
    def extract_data_from_text(self, text):
        """Extrait les données structurées à partir du texte de la facture"""
        from .ocr_service import OCRService
        
        # Extraction basique avec des expressions régulières
        invoice_number = OCRService.extract_invoice_number(text)
        invoice_date = OCRService.extract_date(text)
        total_amount = OCRService.extract_amount(text)
        tax_amount = OCRService.extract_tax_amount(text)
        supplier_name = OCRService.extract_supplier_name(text)
        
        # Calcul du score de confiance (simplifié)
        confidence_score = 0.0
        fields = [invoice_number, invoice_date, total_amount, tax_amount, supplier_name]
        valid_fields = sum(1 for field in fields if field is not None)
        if fields:
            confidence_score = valid_fields / len(fields)
        
        return {
            'invoice_number': invoice_number,
            'invoice_date': invoice_date,
            'total_amount': total_amount,
            'tax_amount': tax_amount,
            'supplier_name': supplier_name,
            'confidence_score': confidence_score
        }
    
    def train_model(self, training_data):
        """Entraîne le modèle avec de nouvelles données"""
        if not training_data:
            logger.warning("Aucune donnée d'entraînement fournie")
            return False
        
        try:
            # Préparation des données
            X = []  # Texte des factures
            y = []  # Données structurées corrigées
            
            for data in training_data:
                X.append(data.get('text', ''))
                y.append(json.dumps(data.get('corrected_data', {})))
            
            # Division des données en ensembles d'entraînement et de test
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Entraînement du modèle
            self.invoice_classifier.fit(X_train, y_train)
            
            # Évaluation du modèle
            y_pred = self.invoice_classifier.predict(X_test)
            accuracy = accuracy_score([json.loads(y) for y in y_test], [json.loads(y) for y in y_pred])
            
            logger.info(f"Modèle entraîné avec une précision de {accuracy:.2f}")
            
            # Sauvegarde du modèle
            self._save_model(self.invoice_classifier, 'invoice_classifier.pkl')
            
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'entraînement du modèle: {str(e)}")
            return False
    
    def predict(self, text):
        """Prédit les données structurées à partir du texte de la facture"""
        # Pour l'instant, on utilise l'extraction basique
        # Dans une implémentation plus avancée, on utiliserait le modèle entraîné
        return self.extract_data_from_text(text)