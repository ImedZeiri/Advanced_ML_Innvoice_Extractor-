from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'suppliers', views.SupplierViewSet)
router.register(r'invoices', views.InvoiceViewSet)
router.register(r'invoice-items', views.InvoiceItemViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('', include(router.urls)),
    path('upload-invoice/', views.upload_invoice, name='upload-invoice'),
    path('save-invoice/', views.save_invoice_with_corrections, name='save-invoice'),
    path('model-stats/', views.get_model_stats, name='model-stats'),
]