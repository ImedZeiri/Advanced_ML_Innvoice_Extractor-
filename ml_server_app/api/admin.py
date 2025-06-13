from django.contrib import admin
from .models import Supplier, Invoice, InvoiceItem, MLModel, TrainingData

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'tax_id', 'created_at')
    search_fields = ('name', 'tax_id')

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'supplier', 'date', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'date')
    search_fields = ('invoice_number', 'supplier__name')
    inlines = [InvoiceItemInline]

@admin.register(MLModel)
class MLModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'version', 'accuracy', 'is_active', 'created_at')
    list_filter = ('is_active',)

@admin.register(TrainingData)
class TrainingDataAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'used_for_training', 'created_at')
    list_filter = ('used_for_training',)