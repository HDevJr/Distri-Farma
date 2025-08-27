from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrRepresentante(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser:
            return True
        if user.groups.filter(name='Representante').exists():
            return True
        return False
