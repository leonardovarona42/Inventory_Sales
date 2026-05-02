from django.urls import path

from . import views

urlpatterns = [
    path("movements/", views.MovimientoListView.as_view(), name="movimiento_list"),
    path("low-stock/", views.LowStockListView.as_view(), name="low_stock"),
]