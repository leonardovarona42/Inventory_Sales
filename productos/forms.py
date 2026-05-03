from django import forms
from .models import Proveedor, Producto, Categoria


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'contacto']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre del proveedor'}),
            'contacto': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Telefono o email'}),
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'unidad_medida', 'stock_actual', 'stock_minimo', 
                  'precio_costo', 'precio_venta', 'imagen', 'proveedor', 'categorias']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nombre del producto'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Descripcion'}),
            'unidad_medida': forms.Select(attrs={'class': 'form-input'}),
            'stock_actual': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'stock_minimo': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'precio_costo': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'imagen': forms.FileInput(attrs={'class': 'form-input', 'accept': 'image/*'}),
            'proveedor': forms.Select(attrs={'class': 'form-input'}),
            'categorias': forms.SelectMultiple(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proveedor'].required = False
