from django.urls import path
from . import views

urlpatterns = [
    path("activar-licencia/", views.activar_licencia_view, name="activar_licencia"),
    path("activar-licencia/procesar/", views.procesar_activacion, name="procesar_activacion"),
    path("acerca-de/", views.acerca_de_view, name="acerca_de"),
    path("acerca-de/renovar/", views.renovar_licencia_view, name="renovar_licencia"),
]
