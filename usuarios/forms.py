from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from .models import UsuarioPerfil


class UsuarioForm(forms.ModelForm):
    """Formulario para crear/editar usuarios del sistema"""
    GRUPOS = [
        ('Superadmin', 'Superadmin - Dueño del negocio'),
        ('Administrador', 'Administrador - Gestión de inventario'),
        ('Cajero', 'Cajero - Punto de venta'),
    ]
    
    grupo = forms.ChoiceField(choices=GRUPOS, required=True, label='Rol')
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        required=False,
        label='Contraseña',
        help_text='Solo requerido al crear un nuevo usuario'
    )
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get current group if editing
        if self.instance.pk:
            current_groups = self.instance.groups.values_list('name', flat=True)
            if current_groups:
                self.fields['grupo'].initial = current_groups.first()

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Este nombre de usuario ya existe')
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        # Assign group
        grupo = self.cleaned_data.get('grupo')
        if grupo:
            try:
                group = Group.objects.get(name=grupo)
                user.groups.clear()
                user.groups.add(group)
            except Group.DoesNotExist:
                Group.objects.create(name=grupo)
                user.groups.add(Group.objects.get(name=grupo))
        return user


class CambiarPasswordForm(forms.Form):
    """Formulario para cambiar contraseña"""
    password_actual = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        label='Contraseña actual'
    )
    password_nuevo = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        label='Nueva contraseña'
    )
    password_confirmar = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input'}),
        label='Confirmar nueva contraseña'
    )

    def clean(self):
        cleaned_data = super().clean()
        nuevo = cleaned_data.get('password_nuevo')
        confirmar = cleaned_data.get('password_confirmar')
        if nuevo and confirmar and nuevo != confirmar:
            raise forms.ValidationError('Las contraseñas no coinciden')
        return cleaned_data
