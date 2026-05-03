from django.urls import path
from . import views

urlpatterns = [
    path('', views.UsuarioListView.as_view(), name='usuario_list'),
    path('create/', views.UsuarioCreateView.as_view(), name='usuario_create'),
    path('<int:pk>/update/', views.UsuarioUpdateView.as_view(), name='usuario_update'),
    path('<int:pk>/delete/', views.UsuarioDeleteView.as_view(), name='usuario_delete'),
    path('<int:pk>/toggle/', views.activar_desactivar_usuario, name='usuario_toggle'),
    path('mi-perfil/', views.mi_perfil, name='mi_perfil'),
    path('cambiar-password/', views.cambiar_password, name='cambiar_password'),
]
