"""sapevo_m_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='/'),
    path('metodo/', views.metodo, name='metodo'),
    path('projeto/<projeto_id>/', views.projeto, name='projeto'),
    path('cadastradecisores/<projeto_id>/', views.cadastradecisores, name='cadastradecisores'),
    path('cadastraalternativas/<projeto_id>/', views.cadastraalternativas, name='cadastraalternativas'),
    path('cadastracriterios/<projeto_id>/', views.cadastracriterios, name='cadastracriterios'),
    path('avaliarcriterios/<projeto_id>/', views.avaliarcriterios, name='avaliarcriterios'),
    path('avaliaralternativas/<projeto_id>/', views.avaliaralternativas, name='avaliaralternativas'),
    path('resultado/<projeto_id>/', views.resultado, name='resultado'),
    path('editardados/', views.editardados, name='editardados'),
    path('deletarprojeto/<projeto_id>/', views.deletarprojeto, name='deletarprojeto'),
]
