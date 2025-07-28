"""
Configurações de administração para o modelo de usuário customizado.
Define como o modelo UsuarioCustom será exibido e gerenciado no site de administração do Django.
"""

from django.contrib import admin
from .models import UsuarioCustom

# Register your models here.
admin.site.register(UsuarioCustom)
