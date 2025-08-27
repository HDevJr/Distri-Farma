from rest_framework.permissions import BasePermission

class IsAdminOrRepresentanteVenda(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser:
            return True
        if user.groups.filter(name='Representante').exists():
            if view.action == 'create' or view.action == 'list' or view.action == 'retrieve':
                return True
        return False
