from django.contrib import admin
from rest_framework.routers import DefaultRouter
from produtos.views import ProdutoViewSet
from clientes.views import ClienteViewSet
from vendas.views import VendaViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'produtos', ProdutoViewSet)
router.register(r'clientes', ClienteViewSet)
router.register(r'vendas', VendaViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', include('core.urls')),  
    path('usuarios/', include('usuarios.urls')),  

    path('clientes/', include('clientes.urls')),
    path('produtos/', include('produtos.urls')),
    path('vendas/', include('vendas.urls')),
    
    path('api/', include('rest_framework.urls')),
    path('select2/', include('django_select2.urls')),
]
