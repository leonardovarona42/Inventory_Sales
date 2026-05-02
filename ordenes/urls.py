from django.urls import path
from . import views

urlpatterns = [
    path('', views.OrdenListView.as_view(), name='orden_list'),
    path('create/', views.OrdenCreateView.as_view(), name='orden_create'),
    path('pos/', views.POSView.as_view(), name='pos'),
]
