from django.urls import path
from . import views

urlpatterns = [
    # Proveedores
    path('proveedores/', views.ProveedorListView.as_view(), name='proveedor_list'),
    path('proveedores/create/', views.ProveedorCreateView.as_view(), name='proveedor_create'),
    path('proveedores/<int:pk>/update/', views.ProveedorUpdateView.as_view(), name='proveedor_update'),
    path('proveedores/<int:pk>/delete/', views.ProveedorDeleteView.as_view(), name='proveedor_delete'),
    
    # Productos
    path('products/', views.ProductoListView.as_view(), name='producto_list'),
    path('products/create/', views.ProductoCreateView.as_view(), name='producto_create'),
    path('products/<int:pk>/', views.ProductoDetailView.as_view(), name='producto_detail'),
    path('products/<int:pk>/update/', views.ProductoUpdateView.as_view(), name='producto_update'),
    path('products/<int:pk>/delete/', views.ProductoDeleteView.as_view(), name='producto_delete'),
]
