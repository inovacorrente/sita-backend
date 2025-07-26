"""
Modelos e gerenciador de usuários customizados para o sistema.
Inclui o modelo UsuarioCustom e o CustomUserManager.
"""

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.db import models
from .utils import gerar_matricula_para_usuario

# Create your models here.


class CustomUserManager(BaseUserManager):
    """
    Manager personalizado para o modelo de usuário customizado.
    Fornece métodos para criar usuários e superusuários.
    """
    def create_user(self, email, nome_completo, matricula=None, password=None, **extra_fields):  # noqa
        """
        Cria e retorna um novo usuário com os dados fornecidos.

        Args:
            email (str): Email do usuário.
            nome_completo (str): Nome completo do usuário.
            matricula (str, opcional): Matrícula do usuário. Gerada automaticamente se não fornecida.
            password (str, opcional): Senha do usuário.
            **extra_fields: Campos adicionais para o usuário.

        Returns:
            UsuarioCustom: Instância do usuário criado.

        Raises:
            ValueError: Se o campo email não for fornecido.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        # Gera matrícula se não for informada
        if not matricula:
            matricula = gerar_matricula_para_usuario(
                type('TempUser', (), {
                    'email': email,
                    'nome_completo': nome_completo,
                    'is_superuser': extra_fields.get('is_superuser', False),
                    'groups': []  # Não há grupos ainda na criação
                })(),
                self.model
            )
        user = self.model(email=email, nome_completo=nome_completo,
                          matricula=matricula, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nome_completo, password=None, **extra_fields):  # noqa
        """
        Cria e retorna um novo superusuário com os dados fornecidos.

        Args:
            email (str): Email do superusuário.
            nome_completo (str): Nome completo do superusuário.
            password (str, opcional): Senha do superusuário.
            **extra_fields: Campos adicionais para o superusuário.

        Returns:
            UsuarioCustom: Instância do superusuário criado.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(
            email,
            nome_completo,
            password=password,
            **extra_fields
        )


class UsuarioCustom(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuário customizado para o sistema.

    Representa um usuário com campos personalizados, como matrícula, nome completo, CPF, telefone, entre outros.
    """
    matricula = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Matrícula única do usuário. Gerada automaticamente se não informada."
    )
    nome_completo = models.CharField(
        max_length=255,
        help_text="Nome completo do usuário."
    )
    email = models.EmailField(
        unique=True,
        help_text="Endereço de e-mail único do usuário."
    )
    cpf = models.CharField(
        max_length=11,
        unique=True,
        help_text="CPF único do usuário (apenas números)."
    )
    telefone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Telefone do usuário (opcional)."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indica se o usuário está ativo."
    )
    is_staff = models.BooleanField(
        default=False,
        help_text="Indica se o usuário tem acesso ao site de administração."
    )
    is_superuser = models.BooleanField(
        default=False,
        help_text="Indica se o usuário possui todas as permissões."
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        help_text="Data de criação do usuário."
    )
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
        """
        Salva o usuário no banco de dados.
        Gera a matrícula automaticamente se não informada.
        """
        if not self.matricula:
            self.matricula = gerar_matricula_para_usuario(self, self.__class__)
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Retorna a representação em string do usuário (email).
        """
        return self.email
