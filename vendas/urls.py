from django.urls import path
from . import views

urlpatterns = [
    path('', views.venda_list, name='venda_list'),
    path('add/', views.venda_add, name='venda_add'),
    path('edit/<int:pk>/', views.venda_edit, name='venda_edit'),
    path('delete/<int:pk>/', views.venda_delete, name='venda_delete'),
    path('<int:pk>/pdf/', views.venda_pdf, name='venda_pdf'),
    path('<int:pk>/detalhe/', views.venda_detail, name='venda_detail'),
]
