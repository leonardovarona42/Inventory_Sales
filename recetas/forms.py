from django import forms
from django.forms import inlineformset_factory
from .models import ProductoFinal, Receta, DetalleReceta


class ProductoFinalForm(forms.ModelForm):
    class Meta:
        model = ProductoFinal
        fields = ['nombre', 'descripcion', 'precio_base', 'umbral_demanda_alta', 'incremento_por_demanda', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto final'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción'}),
            'precio_base': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Precio base', 'step': '0.01'}),
            'umbral_demanda_alta': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Umbral de demanda'}),
            'incremento_por_demanda': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Incremento %', 'step': '0.01'}),
            'imagen': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }


class RecetaForm(forms.ModelForm):
    class Meta:
        model = Receta
        fields = ['instrucciones']
        widgets = {
            'instrucciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Instrucciones de preparación'}),
        }


class DetalleRecetaForm(forms.ModelForm):
    class Meta:
        model = DetalleReceta
        fields = ['producto', 'cantidad_necesaria']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_necesaria': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad necesaria', 'step': '0.01'}),
        }


# Formset for managing recipe details
DetalleRecetaFormSet = inlineformset_factory(
    Receta, 
    DetalleReceta, 
    form=DetalleRecetaForm,
    extra=1,
    can_delete=True
)
