from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import Invoice, Supplier, InvoiceItem, TrainingData
from .serializers import (
    InvoiceSerializer, SupplierSerializer, 
    InvoiceItemSerializer, TrainingDataSerializer
)
import os
import json
from .services.ocr_service import OCRService
from .services.ml_service import MLService

# Initialisation du service ML
ml_service = MLService()

# Create your views here.
def index(request):
    return JsonResponse({
        'status': 'success',
        'message': 'API ML Server is running'
    })

class SupplierViewSet(viewsets.ModelViewSet):
    """API endpoint pour les fournisseurs"""
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    """API endpoint pour les factures"""
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    parser_classes = [MultiPartParser, FormParser]
    
    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload(self, request):
        """Endpoint pour uploader et traiter une facture"""
        if 'file' not in request.FILES:
            return Response({'error': 'Aucun fichier fourni'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        
        # Création de l'objet facture
        invoice = Invoice(
            file=file,
            original_filename=file.name,
            status='processing'
        )
        invoice.save()
        
        try:
            # Extraction du texte
            file_path = invoice.file.path
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.pdf':
                text = OCRService.extract_text_from_pdf(file_path)
            else:
                from PIL import Image
                image = Image.open(file_path)
                text = OCRService.extract_text_from_image(image)
            
            # Extraction des données avec ML
            extracted_data = ml_service.extract_data_from_text(text)
            
            # Mise à jour de la facture avec les données extraites
            if extracted_data.get('supplier_name'):
                supplier, created = Supplier.objects.get_or_create(
                    name=extracted_data['supplier_name']
                )
                invoice.supplier = supplier
            
            invoice.invoice_number = extracted_data.get('invoice_number')
            invoice.total_amount = extracted_data.get('total_amount')
            invoice.tax_amount = extracted_data.get('tax_amount')
            invoice.confidence_score = extracted_data.get('confidence_score', 0.0)
            
            # Conversion de la date si elle existe
            if extracted_data.get('invoice_date'):
                from datetime import datetime
                try:
                    # Tentative de conversion de la date (format simplifié)
                    date_str = extracted_data['invoice_date']
                    if '/' in date_str:
                        day, month, year = date_str.split('/')
                    elif '-' in date_str:
                        day, month, year = date_str.split('-')
                    else:
                        day, month, year = None, None, None
                    
                    if day and month and year:
                        if len(year) == 2:
                            year = '20' + year
                        invoice.invoice_date = datetime(int(year), int(month), int(day)).date()
                except Exception as e:
                    print(f"Erreur lors de la conversion de la date: {str(e)}")
            
            invoice.status = 'processed'
            invoice.save()
            
            # Création des données d'entraînement
            TrainingData.objects.create(
                invoice=invoice,
                original_extraction=extracted_data,
                corrected_data=extracted_data  # Initialement identique
            )
            
            # Retour des données extraites
            serializer = InvoiceSerializer(invoice)
            return Response({
                'invoice': serializer.data,
                'extracted_text': text,
                'extracted_data': extracted_data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            invoice.status = 'error'
            invoice.save()
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """Endpoint pour valider et corriger les données extraites"""
        invoice = self.get_object()
        corrected_data = request.data.get('corrected_data', {})
        
        # Mise à jour de la facture avec les données corrigées
        if corrected_data.get('supplier_name'):
            supplier, created = Supplier.objects.get_or_create(
                name=corrected_data['supplier_name']
            )
            invoice.supplier = supplier
        
        invoice.invoice_number = corrected_data.get('invoice_number', invoice.invoice_number)
        invoice.total_amount = corrected_data.get('total_amount', invoice.total_amount)
        invoice.tax_amount = corrected_data.get('tax_amount', invoice.tax_amount)
        
        # Conversion de la date si elle existe
        if corrected_data.get('invoice_date'):
            from datetime import datetime
            try:
                # Tentative de conversion de la date (format simplifié)
                date_str = corrected_data['invoice_date']
                if '/' in date_str:
                    day, month, year = date_str.split('/')
                elif '-' in date_str:
                    day, month, year = date_str.split('-')
                else:
                    day, month, year = None, None, None
                
                if day and month and year:
                    if len(year) == 2:
                        year = '20' + year
                    invoice.invoice_date = datetime(int(year), int(month), int(day)).date()
            except Exception as e:
                print(f"Erreur lors de la conversion de la date: {str(e)}")
        
        invoice.status = 'validated'
        invoice.save()
        
        # Mise à jour des données d'entraînement
        try:
            training_data = TrainingData.objects.get(invoice=invoice)
            training_data.corrected_data = corrected_data
            training_data.save()
        except TrainingData.DoesNotExist:
            TrainingData.objects.create(
                invoice=invoice,
                original_extraction={},
                corrected_data=corrected_data
            )
        
        return Response({
            'status': 'success',
            'message': 'Facture validée avec succès'
        })

class InvoiceItemViewSet(viewsets.ModelViewSet):
    """API endpoint pour les lignes de facture"""
    queryset = InvoiceItem.objects.all()
    serializer_class = InvoiceItemSerializer
    
    def get_queryset(self):
        """Filtre les lignes par facture si spécifié"""
        queryset = InvoiceItem.objects.all()
        invoice_id = self.request.query_params.get('invoice', None)
        if invoice_id is not None:
            queryset = queryset.filter(invoice__id=invoice_id)
        return queryset

@api_view(['POST'])
def train_model(request):
    """Endpoint pour entraîner le modèle ML avec les données validées"""
    # Récupération des données d'entraînement non utilisées
    training_data = TrainingData.objects.filter(used_for_training=False)
    
    if not training_data:
        return Response({
            'status': 'error',
            'message': 'Aucune nouvelle donnée d\'entraînement disponible'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Préparation des données pour l'entraînement
    data_for_training = []
    for data in training_data:
        # Récupération du texte extrait de la facture
        file_path = data.invoice.file.path
        file_ext = os.path.splitext(file_path)[1].lower()
        
        if file_ext == '.pdf':
            text = OCRService.extract_text_from_pdf(file_path)
        else:
            from PIL import Image
            image = Image.open(file_path)
            text = OCRService.extract_text_from_image(image)
        
        data_for_training.append({
            'text': text,
            'corrected_data': data.corrected_data
        })
        
        # Marquer comme utilisé pour l'entraînement
        data.used_for_training = True
        data.save()
    
    # Entraînement du modèle
    success = ml_service.train_model(data_for_training)
    
    if success:
        return Response({
            'status': 'success',
            'message': f'Modèle entraîné avec succès sur {len(data_for_training)} exemples'
        })
    else:
        return Response({
            'status': 'error',
            'message': 'Erreur lors de l\'entraînement du modèle'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
