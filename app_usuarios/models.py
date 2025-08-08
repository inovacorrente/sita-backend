"""
Modelos e gerenciador de usuários customizados para o sistema.
Inclui o modelo UsuarioCustom e o CustomUserManager.
"""

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
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
            matricula (str, opcional): Matrícula do usuário.
            Gerada automaticamente se não fornecida.
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
                    'cpf': extra_fields.get('cpf', ''),
                    'is_superuser': extra_fields.get('is_superuser', False),
                    'is_staff': extra_fields.get('is_staff', False),
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
    matricula = models.CharField(max_length=50, unique=True, blank=True)
    nome_completo = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=11, unique=True)
    telefone = models.CharField(max_length=15, blank=True, null=True)
    data_nascimento = models.DateField()
    sexo = models.CharField(
        max_length=1,
        choices=(('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')),
        default='O'
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
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
    REQUIRED_FIELDS = ['email', 'nome_completo', 'data_nascimento']

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
