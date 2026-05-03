from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User, Group
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse

from .forms import UsuarioForm, CambiarPasswordForm


def _es_superadmin(user):
    return user.groups.filter(name="Superadmin").exists()


class SoloSuperadminMixin(UserPassesTestMixin):
    def test_func(self):
        return _es_superadmin(self.request.user)


class UsuarioListView(LoginRequiredMixin, SoloSuperadminMixin, ListView):
    model = User
    template_name = 'usuarios/usuario_list.html'
    context_object_name = 'usuarios'
    paginate_by = 20

    def get_queryset(self):
        return User.objects.prefetch_related('groups', 'perfil').order_by('username')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all available groups
        context['grupos'] = Group.objects.all()
        return context


class UsuarioCreateView(LoginRequiredMixin, SoloSuperadminMixin, CreateView):
    model = User
    form_class = UsuarioForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuario_list')

    def form_valid(self, form):
        messages.success(self.request, f'Usuario {form.cleaned_data["username"]} creado exitosamente')
        return super().form_valid(form)


class UsuarioUpdateView(LoginRequiredMixin, SoloSuperadminMixin, UpdateView):
    model = User
    form_class = UsuarioForm
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuario_list')

    def get_queryset(self):
        return User.objects.prefetch_related('groups')

    def form_valid(self, form):
        messages.success(self.request, f'Usuario {form.cleaned_data["username"]} actualizado exitosamente')
        return super().form_valid(form)


class UsuarioDeleteView(LoginRequiredMixin, SoloSuperadminMixin, DeleteView):
    model = User
    template_name = 'usuarios/usuario_confirm_delete.html'
    success_url = reverse_lazy('usuario_list')

    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        # Prevent deleting yourself
        if user == request.user:
            messages.error(request, 'No puedes eliminar tu propio usuario')
            return redirect('usuario_list')
        messages.success(request, f'Usuario {user.username} eliminado')
        return super().delete(request, *args, **kwargs)


@login_required
def mi_perfil(request):
    """Vista para que el usuario vea su propio perfil"""
    user = request.user
    grupos = user.groups.values_list('name', flat=True)
    return render(request, 'usuarios/mi_perfil.html', {
        'user': user,
        'grupos': list(grupos),
    })


@login_required
def cambiar_password(request):
    """Vista para cambiar la contraseña del usuario logueado"""
    if request.method == 'POST':
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            if not request.user.check_password(form.cleaned_data['password_actual']):
                messages.error(request, 'La contraseña actual es incorrecta')
            else:
                request.user.set_password(form.cleaned_data['password_nuevo'])
                request.user.save()
                messages.success(request, 'Contraseña cambiada exitosamente')
                return redirect('mi_perfil')
    else:
        form = CambiarPasswordForm()
    return render(request, 'usuarios/cambiar_password.html', {'form': form})


@login_required
@require_POST
def activar_desactivar_usuario(request, pk):
    """Activar/desactivar un usuario"""
    if not _es_superadmin(request.user):
        return JsonResponse({"success": False, "error": "No autorizado"}, status=403)

    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        return JsonResponse({"success": False, "error": "No puedes desactivar tu propio usuario"})
    
    user.is_active = not user.is_active
    user.save()
    estado = "activado" if user.is_active else "desactivado"
    return JsonResponse({"success": True, "estado": estado})
