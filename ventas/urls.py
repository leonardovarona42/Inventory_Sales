from django.urls import path
from . import views

urlpatterns = [
    path('', views.VentaListView.as_view(), name='venta_list'),
    path('<int:pk>/', views.VentaDetailView.as_view(), name='venta_detail'),
]
