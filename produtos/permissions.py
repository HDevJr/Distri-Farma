from rest_framework.permissions import BasePermission

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser:
            return True
        if user.groups.filter(name='Representante').exists():
            # Representante só pode ver produtos
            if request.method in ('GET', 'HEAD', 'OPTIONS'):
                return True
        return False
