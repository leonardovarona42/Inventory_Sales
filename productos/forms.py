from django import forms
from django.contrib.auth.models import User
from .models import Proveedor, Producto


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'contacto']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del proveedor'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono o email'}),
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'unidad_medida', 'stock_actual', 'stock_minimo', 'precio_costo', 'proveedor', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'unidad_medida': forms.Select(attrs={'class': 'form-control'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock actual', 'step': '0.01'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock mínimo', 'step': '0.01'}),
            'precio_costo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio de costo', 'step': '0.01'}),
            'proveedor': forms.Select(attrs={'class': 'form-control'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
