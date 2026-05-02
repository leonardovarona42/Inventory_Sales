from django import forms
from .models import Venta, DetalleVenta


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
        fields = ['id_producto_final', 'cantidad']
        widgets = {
            'id_producto_final': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad', 'min': '1'}),
        }
