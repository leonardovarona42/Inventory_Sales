from django import forms
from .models import Orden


class OrdenForm(forms.ModelForm):
    class Meta:
        model = Orden
        fields = ['cliente_nombre', 'cliente_telefono', 'estado', 'notas']
        widgets = {
            'cliente_nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente'}),
            'cliente_telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono del cliente'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notas adicionales'}),
        }


class CambiarEstadoOrdenForm(forms.Form):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('preparando', 'En preparación'),
        ('listo', 'Listo para entregar'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )
    
    estado = forms.ChoiceField(
        choices=ESTADOS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
