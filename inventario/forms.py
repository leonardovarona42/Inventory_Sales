from django import forms
from .models import MovimientoStock
from productos.models import Producto


class AjusteStockForm(forms.Form):
    """Formulario para ajustes manuales de inventario"""
    MOTIVO_CHOICES = [
        (MovimientoStock.AJUSTE, 'Ajuste de inventario'),
        (MovimientoStock.MERMA, 'Merma/Perdida'),
        (MovimientoStock.DEVOLUCION, 'Devolucion'),
    ]

    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter().order_by('nombre'),
        label='Producto',
        widget=forms.Select(attrs={
            'class': 'input-field',
            'id': 'ajusteProducto',
        }),
    )
    tipo = forms.ChoiceField(
        choices=MovimientoStock.TIPOS_MOVIMIENTO,
        widget=forms.RadioSelect(attrs={'class': 'w-4 h-4 text-primary-600'}),
        label='Tipo de ajuste',
        initial='entrada',
    )
    cantidad = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        label='Cantidad',
        widget=forms.NumberInput(attrs={
            'class': 'input-field',
            'step': '0.01',
            'min': '0.01',
            'placeholder': '0.00',
        }),
    )
    motivo = forms.ChoiceField(
        choices=MOTIVO_CHOICES,
        widget=forms.Select(attrs={'class': 'input-field'}),
        label='Motivo',
    )
    notas = forms.CharField(
        required=False,
        label='Observaciones',
        widget=forms.Textarea(attrs={
            'class': 'input-field',
            'rows': 3,
            'placeholder': 'Descripcion del ajuste...',
        }),
    )
