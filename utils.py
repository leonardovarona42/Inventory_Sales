from django.contrib.auth.mixins import UserPassesTestMixin, AccessMixin
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied


def _tiene_rol(user, roles):
    """Verifica si el usuario tiene alguno de los roles especificados."""
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=roles).exists()


class IsAdminUser(UserPassesTestMixin):
    """Mixin que restringe acceso a usuarios staff o en grupos admin."""
    def test_func(self):
        return self.request.user.is_staff or _tiene_rol(self.request.user, ["Administrador", "Superadmin"])


class IsCajeroOrAbove(UserPassesTestMixin):
    """Acceso para Cajero, Administrador o Superadmin."""
    def test_func(self):
        return _tiene_rol(self.request.user, ["Cajero", "Administrador", "Superadmin"])


class IsSuperadmin(UserPassesTestMixin):
    """Acceso solo para Superadmin."""
    def test_func(self):
        return _tiene_rol(self.request.user, ["Superadmin"])


def require_rol(roles):
    """Decorator para restringir vistas por rol."""
    def check(user):
        return _tiene_rol(user, roles)
    return user_passes_test(check)
