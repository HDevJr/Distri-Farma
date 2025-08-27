from rest_framework import viewsets, permissions
from .models import Usuario
from .serializers import UsuarioSerializer, UsuarioCreateSerializer
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer

@login_required
def home(request):
    return render(request, 'core/home.html')