from django import forms
from .models import Proveedor, Producto, Categoria
from django.core.validators import FileExtensionValidator
from django.utils.translation import gettext_lazy as _

INPUT = 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white'


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'icono', 'color', 'orden', 'activa', 'padre']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Nombre de la categoria'}),
            'descripcion': forms.Textarea(attrs={'class': INPUT, 'rows': 3, 'placeholder': 'Descripcion'}),
            'icono': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'fa-box'}),
            'color': forms.TextInput(attrs={'class': INPUT, 'type': 'color', 'style': 'height: 42px; padding: 4px;'}),
            'orden': forms.NumberInput(attrs={'class': INPUT}),
            'activa': forms.CheckboxInput(attrs={'class': 'w-4 h-4 text-primary-600 rounded border-gray-300 dark:border-gray-600 focus:ring-primary-500'}),
            'padre': forms.Select(attrs={'class': INPUT}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['padre'].required = False
        self.fields['padre'].empty_label = 'Sin categoria padre (raiz)'


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
        fields = ['nombre', 'descripcion', 'codigo_barras', 'lote', 'fecha_vencimiento', 'unidad_medida', 'stock_actual', 'stock_minimo',
                  'precio_costo', 'precio_venta', 'imagen', 'proveedor', 'categorias']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'Nombre del producto'}),
            'descripcion': forms.Textarea(attrs={'class': INPUT, 'rows': 3, 'placeholder': 'Descripcion'}),
            'codigo_barras': forms.TextInput(attrs={'class': INPUT, 'placeholder': '7501234567890'}),
            'lote': forms.TextInput(attrs={'class': INPUT, 'placeholder': 'LOTE-001'}),
            'fecha_vencimiento': forms.DateInput(attrs={'class': INPUT, 'type': 'date'}),
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
        self.fields['imagen'].validators.append(
            FileExtensionValidator(
                ['jpg', 'jpeg', 'png', 'gif', 'webp'],
                _("Solo se permiten imagenes (jpg, jpeg, png, gif, webp)")
            )
        )

    def clean_imagen(self):
        imagen = self.cleaned_data.get('imagen')
        if imagen:
            if imagen.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError(_("El archivo es demasiado grande (maximo 5MB)"))
            if not imagen.content_type.startswith('image/'):
                raise forms.ValidationError(_("El archivo debe ser una imagen"))
        return imagen
