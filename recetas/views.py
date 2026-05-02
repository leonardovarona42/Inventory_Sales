from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import ProductoFinal, Receta, DetalleReceta
from .forms import ProductoFinalForm, RecetaForm, DetalleRecetaFormSet


class IsChefOrAdmin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or self.request.user.groups.filter(name='Chef').exists()


class ProductoFinalListView(LoginRequiredMixin, ListView):
    model = ProductoFinal
    template_name = 'recetas/productofinal_list.html'
    context_object_name = 'productos'
    paginate_by = 20


class ProductoFinalCreateView(LoginRequiredMixin, IsChefOrAdmin, CreateView):
    model = ProductoFinal
    form_class = ProductoFinalForm
    template_name = 'recetas/productofinal_form.html'
    success_url = reverse_lazy('productofinal_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        Receta.objects.create(producto_final=self.object)
        messages.success(self.request, 'Producto creado exitosamente')
        return response
