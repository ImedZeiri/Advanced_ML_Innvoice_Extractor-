from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'invoices', views.InvoiceViewSet)
router.register(r'suppliers', views.SupplierViewSet)
router.register(r'invoice-items', views.InvoiceItemViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('', include(router.urls)),
    path('train-model/', views.train_model, name='train-model'),
]