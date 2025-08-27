from django.urls import path
from . import views

urlpatterns = [
    path('', views.cliente_list, name='cliente_list'),
    path('add/', views.cliente_add, name='cliente_add'),
    path('edit/<int:pk>/', views.cliente_edit, name='cliente_edit'),
    path('delete/<int:pk>/', views.cliente_delete, name='cliente_delete'),
]
