from django.contrib import admin
from .models import Invoice, Supplier, InvoiceItem, TrainingData

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'siret', 'created_at')
    search_fields = ('name', 'siret')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'supplier', 'invoice_date', 'total_amount', 'status', 'confidence_score')
    list_filter = ('status', 'invoice_date', 'created_at')
    search_fields = ('invoice_number', 'supplier__name')
    date_hierarchy = 'created_at'

@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'description', 'quantity', 'unit_price', 'total_price')
    list_filter = ('invoice',)
    search_fields = ('description', 'invoice__invoice_number')

@admin.register(TrainingData)
class TrainingDataAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'used_for_training', 'created_at')
    list_filter = ('used_for_training', 'created_at')
    search_fields = ('invoice__invoice_number',)
