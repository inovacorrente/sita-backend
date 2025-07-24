
from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from .utils import gerar_matricula_para_usuario

# Create your models here.


class UsuarioCustom(AbstractBaseUser):
    matricula = models.CharField(max_length=50, unique=True, blank=True)
    nome_completo = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=11, unique=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    username = None  # Removendo campo username

    USERNAME_FIELD = 'matricula'
    REQUIRED_FIELDS = ['email', 'nome_completo', 'matricula']

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'

    def save(self, *args, **kwargs):

        if not self.matricula:
            self.matricula = gerar_matricula_para_usuario(self, self.__class__)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
