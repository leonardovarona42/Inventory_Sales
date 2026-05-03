from django.urls import path
from . import views

urlpatterns = [
    path('proveedores/', views.ProveedorListView.as_view(), name='proveedor_list'),
    path('proveedores/create/', views.ProveedorCreateView.as_view(), name='proveedor_create'),
    path('proveedores/<int:pk>/update/', views.ProveedorUpdateView.as_view(), name='proveedor_update'),
    path('proveedores/<int:pk>/delete/', views.ProveedorDeleteView.as_view(), name='proveedor_delete'),
    path('', views.ProductoListView.as_view(), name='producto_list'),
    path('create/', views.ProductoCreateView.as_view(), name='producto_create'),
    path('<int:pk>/', views.ProductoDetailView.as_view(), name='producto_detail'),
    path('<int:pk>/update/', views.ProductoUpdateView.as_view(), name='producto_update'),
    path('<int:pk>/delete/', views.ProductoDeleteView.as_view(), name='producto_delete'),
]
