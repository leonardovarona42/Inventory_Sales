from django.contrib.auth.mixins import UserPassesTestMixin


class IsAdminUser(UserPassesTestMixin):
    """Mixin que restringe acceso a usuarios staff."""
    def test_func(self):
        return self.request.user.is_staff
