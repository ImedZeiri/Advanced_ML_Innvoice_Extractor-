from django.db import models
from django.utils import timezone

class Supplier(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    tax_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Invoice(models.Model):
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('validated', 'Validée'),
        ('rejected', 'Rejetée'),
    )
    
    invoice_number = models.CharField(max_length=100)
    date = models.DateField()
    due_date = models.DateField(null=True, blank=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='invoices')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    original_file = models.FileField(upload_to='invoices/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.invoice_number} - {self.supplier.name}"

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.description} - {self.invoice.invoice_number}"

class MLModel(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    accuracy = models.FloatField()
    file_path = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} v{self.version}"

class TrainingData(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='training_data')
    original_extraction = models.JSONField()
    corrected_extraction = models.JSONField()
    used_for_training = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Training data for {self.invoice.invoice_number}"
