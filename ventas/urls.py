from django.urls import path
from . import views

urlpatterns = [
    path('', views.VentaListView.as_view(), name='venta_list'),
    path('<int:pk>/', views.VentaDetailView.as_view(), name='venta_detail'),
    path('pos/', views.POSView.as_view(), name='pos'),
    path('pos/ajax/agregar/', views.ajax_agregar_carrito, name='ajax_agregar_carrito'),
    path('pos/ajax/quitar/', views.ajax_quitar_carrito, name='ajax_quitar_carrito'),
    path('pos/ajax/limpiar/', views.ajax_limpiar_carrito, name='ajax_limpiar_carrito'),
    path('pos/ajax/procesar/', views.ajax_procesar_venta, name='ajax_procesar_venta'),
    path('<int:pk>/cancelar/', views.ajax_cancelar_venta, name='venta_cancelar'),
]
