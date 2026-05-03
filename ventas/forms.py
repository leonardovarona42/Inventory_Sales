from django import forms
from .models import Venta, DetalleVenta
from productos.models import Producto


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
        # Only show final products
        self.fields['id_producto'].queryset = Producto.objects.filter(tipo_producto='final')
