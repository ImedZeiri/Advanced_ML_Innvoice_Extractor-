import os
import json
import tempfile
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.conf import settings
from django.db import transaction
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, parser_classes, action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Invoice, Supplier, InvoiceItem, MLModel, TrainingData
from .serializers import (
    InvoiceSerializer, 
    SupplierSerializer, 
    InvoiceItemSerializer,
    MLModelSerializer,
    TrainingDataSerializer,
    InvoiceUploadSerializer
)
from .ml_processor import (
    extract_text_from_pdf,
    extract_text_from_image,
    process_invoice_data,
    train_model_with_corrections
)

# Index view
@api_view(['GET'])
def index(request):
    return Response({
        'status': 'success',
        'message': 'API ML Server is running'
    })

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        invoice = self.get_object()
        items = invoice.items.all()
        serializer = InvoiceItemSerializer(items, many=True)
        return Response(serializer.data)

class InvoiceItemViewSet(viewsets.ModelViewSet):
    queryset = InvoiceItem.objects.all()
    serializer_class = InvoiceItemSerializer
    
    def get_queryset(self):
        queryset = InvoiceItem.objects.all()
        invoice_id = self.request.query_params.get('invoice_id', None)
        if invoice_id is not None:
            queryset = queryset.filter(invoice_id=invoice_id)
        return queryset

@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_invoice(request):
    """
    Upload and process an invoice file (PDF or image)
    """
    serializer = InvoiceUploadSerializer(data=request.data)
    
    if serializer.is_valid():
        invoice_file = serializer.validated_data['file']
        
        try:
            # Pour cette version simplifiée, nous n'avons pas besoin de traiter le fichier réel
            # Nous utilisons directement la fonction process_invoice_data avec un texte simulé
            extracted_text = extract_text_from_pdf(None)  # Utilise le texte simulé
            
            # Process the extracted text with rule-based approach
            extracted_data = process_invoice_data(extracted_text)
            
            return Response({
                'status': 'success',
                'extracted_data': extracted_data,
                'original_text': extracted_text[:1000]  # Limit text size in response
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@parser_classes([JSONParser])
def save_invoice_with_corrections(request):
    """
    Save invoice data with user corrections and use it for training
    """
    try:
        with transaction.atomic():
            data = request.data
            
            # Get or create supplier
            supplier_data = data.get('supplier', {})
            supplier, created = Supplier.objects.get_or_create(
                name=supplier_data.get('name'),
                defaults={
                    'address': supplier_data.get('address', ''),
                    'tax_id': supplier_data.get('tax_id', '')
                }
            )
            
            # Create invoice
            invoice_data = data.get('invoice', {})
            invoice = Invoice.objects.create(
                invoice_number=invoice_data.get('invoice_number'),
                date=invoice_data.get('date'),
                due_date=invoice_data.get('due_date'),
                supplier=supplier,
                total_amount=invoice_data.get('total_amount'),
                tax_amount=invoice_data.get('tax_amount', 0),
                status='validated',
                original_file=request.data.get('file_path', '')
            )
            
            # Create invoice items
            items_data = data.get('items', [])
            for item_data in items_data:
                InvoiceItem.objects.create(
                    invoice=invoice,
                    description=item_data.get('description'),
                    quantity=item_data.get('quantity'),
                    unit_price=item_data.get('unit_price'),
                    total_price=item_data.get('total_price'),
                    tax_rate=item_data.get('tax_rate', 0)
                )
            
            # Save training data
            original_extraction = data.get('original_extraction', {})
            corrected_extraction = {
                'invoice': invoice_data,
                'supplier': supplier_data,
                'items': items_data
            }
            
            training_data = TrainingData.objects.create(
                invoice=invoice,
                original_extraction=original_extraction,
                corrected_extraction=corrected_extraction
            )
            
            # Trigger async model training (in a real app, this would be a background task)
            train_model_with_corrections(training_data.id)
            
            return Response({
                'status': 'success',
                'message': 'Invoice saved successfully and will be used for training',
                'invoice_id': invoice.id
            })
            
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_model_stats(request):
    """
    Get statistics about the ML model and training data
    """
    try:
        active_model = MLModel.objects.filter(is_active=True).first()
        total_invoices = Invoice.objects.count()
        training_data_count = TrainingData.objects.count()
        used_for_training = TrainingData.objects.filter(used_for_training=True).count()
        
        return Response({
            'status': 'success',
            'active_model': MLModelSerializer(active_model).data if active_model else None,
            'total_invoices': total_invoices,
            'training_data_count': training_data_count,
            'used_for_training': used_for_training,
            'pending_training': training_data_count - used_for_training
        })
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
