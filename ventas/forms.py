from django import forms
from .models import Venta, DetalleVenta, Cliente, ConfiguracionSistema
from productos.models import Producto


class ConfiguracionForm(forms.ModelForm):
    class Meta:
        model = ConfiguracionSistema
        fields = [
            'nombre_negocio', 'rnc_negocio', 'direccion', 'telefono', 'email',
            'simbolo_moneda', 'tasa_impuesto', 'mensaje_recibo_superior',
            'mensaje_recibo_inferior', 'pie_pagina', 'logo',
        ]
        widgets = {
            'nombre_negocio': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Mi Negocio'}),
            'rnc_negocio': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'RNC'}),
            'direccion': forms.Textarea(attrs={'class': 'input-field', 'rows': 2, 'placeholder': 'Direccion del negocio'}),
            'telefono': forms.TextInput(attrs={'class': 'input-field', 'placeholder': '+1 XXX XXX XXXX'}),
            'email': forms.EmailInput(attrs={'class': 'input-field', 'placeholder': 'correo@negocio.com'}),
            'simbolo_moneda': forms.TextInput(attrs={'class': 'input-field w-20', 'placeholder': 'RD$'}),
            'tasa_impuesto': forms.NumberInput(attrs={'class': 'input-field w-24', 'step': '0.01', 'min': '0', 'max': '100'}),
            'mensaje_recibo_superior': forms.Textarea(attrs={'class': 'input-field', 'rows': 2, 'placeholder': 'Bienvenido a...'}),
            'mensaje_recibo_inferior': forms.Textarea(attrs={'class': 'input-field', 'rows': 2, 'placeholder': 'Gracias por su compra...'}),
            'pie_pagina': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Gracias por su compra'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'input-field'}),
        }


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'email', 'telefono', 'direccion', 'rnc', 'notas', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={'class': 'input-field', 'placeholder': 'correo@ejemplo.com'}),
            'telefono': forms.TextInput(attrs={'class': 'input-field', 'placeholder': '+53 XXXX XXXX'}),
            'direccion': forms.Textarea(attrs={'class': 'input-field', 'rows': 2, 'placeholder': 'Direccion completa'}),
            'rnc': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'RNC o CI'}),
            'notas': forms.Textarea(attrs={'class': 'input-field', 'rows': 2, 'placeholder': 'Notas adicionales'}),
            'activa': forms.CheckboxInput(attrs={'class': 'rounded'}),
        }


class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['metodo_pago']
        widgets = {
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
        }


class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['id_producto', 'cantidad']
        widgets = {
            'id_producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad', 'min': '1'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_producto'].queryset = Producto.objects.filter(stock_actual__gt=0).order_by('nombre')
