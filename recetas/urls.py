from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductoFinalListView.as_view(), name='productofinal_list'),
    path('create/', views.ProductoFinalCreateView.as_view(), name='productofinal_create'),
]
