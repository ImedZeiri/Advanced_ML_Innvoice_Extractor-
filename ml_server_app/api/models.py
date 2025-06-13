from django.db import models
from django.utils import timezone
import os
import uuid

def invoice_upload_path(instance, filename):
    """Génère un chemin unique pour chaque facture uploadée"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('invoices', filename)

class Supplier(models.Model):
    """Modèle pour les fournisseurs"""
    name = models.CharField(max_length=255)
    siret = models.CharField(max_length=14, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Invoice(models.Model):
    """Modèle pour les factures"""
    STATUS_CHOICES = (
        ('pending', 'En attente de traitement'),
        ('processing', 'En cours de traitement'),
        ('processed', 'Traitée'),
        ('error', 'Erreur'),
        ('validated', 'Validée'),
    )
    
    file = models.FileField(upload_to=invoice_upload_path)
    original_filename = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    invoice_number = models.CharField(max_length=100, blank=True, null=True)
    invoice_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    confidence_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Facture {self.invoice_number or self.id}"

class InvoiceItem(models.Model):
    """Modèle pour les lignes de facture"""
    invoice = models.ForeignKey(Invoice, related_name='items', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)
    
    def __str__(self):
        return f"{self.description} ({self.invoice})"

class TrainingData(models.Model):
    """Modèle pour stocker les données d'entraînement du modèle ML"""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    original_extraction = models.JSONField()
    corrected_data = models.JSONField()
    used_for_training = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Données d'entraînement pour {self.invoice}"
