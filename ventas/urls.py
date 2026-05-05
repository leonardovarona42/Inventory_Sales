from django.urls import path
from . import views

urlpatterns = [
    path('', views.VentaListView.as_view(), name='venta_list'),
    path('<int:pk>/', views.VentaDetailView.as_view(), name='venta_detail'),
    path('<int:pk>/cancelar/', views.ajax_cancelar_venta, name='venta_cancelar'),
    path('pos/', views.POSView.as_view(), name='pos'),
    path('pos/ajax/agregar/', views.ajax_agregar_carrito, name='ajax_agregar_carrito'),
    path('pos/ajax/quitar/', views.ajax_quitar_carrito, name='ajax_quitar_carrito'),
    path('pos/ajax/limpiar/', views.ajax_limpiar_carrito, name='ajax_limpiar_carrito'),
    path('pos/ajax/procesar/', views.ajax_procesar_venta, name='ajax_procesar_venta'),
    path('pos/ajax/buscar-cliente/', views.ajax_buscar_cliente, name='ajax_buscar_cliente'),
    path('pos/ajax/crear-cliente/', views.ajax_crear_cliente, name='cliente_create_ajax'),
    path('clientes/', views.ClienteListView.as_view(), name='cliente_list'),
    path('clientes/nuevo/', views.ClienteCreateView.as_view(), name='cliente_create'),
    path('clientes/<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente_update'),
    path('clientes/<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='cliente_delete'),
    path('configuracion/', views.ConfiguracionUpdateView.as_view(), name='configuracion_update'),
]
