from django.urls import path
from . import views

urlpatterns = [
    path('', views.produto_list, name='produto_list'),
    path('add/', views.produto_add, name='produto_add'),
    path('edit/<int:pk>/', views.produto_edit, name='produto_edit'),
    path('delete/<int:pk>/', views.produto_delete, name='produto_delete'),
    path('valor-unitario/', views.valor_unitario_view, name='valor_unitario'),
]
