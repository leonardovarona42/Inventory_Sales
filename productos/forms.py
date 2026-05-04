from django import forms
from .models import Proveedor, Producto, Categoria

INPUT = 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white'


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'contacto']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Nombre del proveedor'}),
            'contacto': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Telefono o email'}),
        }


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'unidad_medida', 'stock_actual', 'stock_minimo',
                  'precio_costo', 'precio_venta', 'imagen', 'proveedor', 'categorias']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Nombre del producto'}),
            'descripcion': forms.Textarea(attrs={'class': INPUT, 'rows': 3, 'placeholder': 'Descripcion'}),
            'unidad_medida': forms.Select(attrs={'class': INPUT}),
            'stock_actual': forms.NumberInput(attrs={'class': INPUT, 'step': '0.01'}),
            'stock_minimo': forms.NumberInput(attrs={'class': INPUT, 'step': '0.01'}),
            'precio_costo': forms.NumberInput(attrs={'class': INPUT, 'step': '0.01', 'placeholder': '0.00'}),
            'precio_venta': forms.NumberInput(attrs={'class': INPUT, 'step': '0.01', 'placeholder': '0.00'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'hidden', 'accept': 'image/*'}),
            'proveedor': forms.Select(attrs={'class': INPUT}),
            'categorias': forms.CheckboxSelectMultiple(attrs={'class': 'hidden'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proveedor'].required = False
        self.fields['categorias'].help_text = None
