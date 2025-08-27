from django.urls import path
from . import views

urlpatterns = [
    path('', views.orcamento_list, name='orcamento_list'),
    path('novo/', views.orcamento_add, name='orcamento_add'),
    path('<int:pk>/editar/', views.orcamento_edit, name='orcamento_edit'),
    path('<int:pk>/pdf/', views.orcamento_pdf, name='orcamento_pdf'),
    path('<int:pk>/confirmar/', views.orcamento_confirmar_conversao, name='orcamento_confirmar_conversao'),
    path('<int:pk>/converter/', views.orcamento_converter, name='orcamento_converter'),
    path('<int:pk>/delete/', views.orcamento_delete, name='orcamento_delete'),
    path('<int:pk>/detalhe/', views.orcamento_detail, name='orcamento_detail'),
]