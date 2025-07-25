
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models

from .utils import gerar_matricula_para_usuario

# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, email, nome_completo, matricula=None, password=None, **extra_fields):  # noqa
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, nome_completo=nome_completo,
                          matricula=matricula, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome_completo, password=None, **extra_fields):  # noqa
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, nome_completo, None, password, **extra_fields)  # noqa


class UsuarioCustom(AbstractBaseUser, PermissionsMixin):
    matricula = models.CharField(max_length=50, unique=True, blank=True)
    nome_completo = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=11, unique=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='usuario_custom_set',
        blank=True,
        verbose_name='groups',
        help_text='Os grupos aos quais este usuário pertence.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='usuario_custom_set',
        blank=True,
        verbose_name='user permissions',
        help_text='Permissões específicas para este usuário.',
    )

    username = None  # Removendo campo username

    USERNAME_FIELD = 'matricula'
    REQUIRED_FIELDS = ['email', 'nome_completo']

    objects = CustomUserManager()

    class Meta:
        verbose_name = 'usuário'
        verbose_name_plural = 'usuários'

    def save(self, *args, **kwargs):

        if not self.matricula:
            self.matricula = gerar_matricula_para_usuario(self, self.__class__)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
