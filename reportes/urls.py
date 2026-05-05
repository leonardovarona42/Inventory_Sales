from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('inventario-valoracion/', views.InventarioValoracionView.as_view(), name='inventario_valoracion'),
    path('inventario-valoracion/export/', views.export_valoracion_csv, name='inventario_valoracion_export'),
]
