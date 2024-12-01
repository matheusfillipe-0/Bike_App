from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.utils import timezone
import re
from django.conf import settings


# Validadores
cpf_validator = RegexValidator(r'^\d{3}\.\d{3}\.\d{3}\-\d{2}$', 'CPF inválido')
numero_cartao_validator = RegexValidator(r'^\d{16}$', 'Número de cartão inválido')
validade_cartao_validator = RegexValidator(r'^\d{2}/\d{4}$', 'Formato de validade inválido. Use MM/AAAA.')

class UsuarioManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O campo Email deve ser informado')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True)
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=14, unique=True, validators=[cpf_validator], null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    data_nascimento = models.DateField(null=True, blank=True)
    
    # Endereço
    logradouro = models.CharField(max_length=255)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=100)
    cidade = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    cep = models.CharField(max_length=10)
    
    # Deficiência
    possui_deficiencia = models.BooleanField(default=False)
    deficiencia = models.CharField(max_length=100, null=True, blank=True)
    
    # Usuário
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UsuarioManager()

    def __str__(self):
        return self.nome

    def clean(self):
         
        if self.cpf:
            cpf = self.cpf.replace('.', '').replace('-', '')
            if not re.match(r'^\d{11}$', cpf):
                raise ValidationError('CPF deve ter 11 dígitos numéricos.')
        super().clean()

class Pagamento(models.Model):
    CARTAO = 'cartao'
    TRANSPORTE = 'transporte_publico'

    FORMAS_PAGAMENTO = [
        (CARTAO, 'Cartão de Crédito/Débito'),
        (TRANSPORTE, 'Cartão de Transporte Público'),
    ]
    
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pagamentos')
    forma_pagamento = models.CharField(max_length=20, choices=FORMAS_PAGAMENTO)
    cartao = models.ForeignKey('Cartao', on_delete=models.SET_NULL, null=True, blank=True, related_name='pagamentos')

    def __str__(self):
        return f"Pagamento {self.id} - {self.usuario.nome}"

    def clean(self):
        if self.forma_pagamento == self.CARTAO and not self.cartao:
            raise ValidationError("O cartão de crédito deve ser informado.")
        super().clean()

 
class Estacao(models.Model):
    nome = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.nome

class Bicicleta(models.Model):
    estacao = models.ForeignKey(Estacao, on_delete=models.CASCADE, related_name="bicicletas")
    status = models.CharField(max_length=20, choices=[('disponivel', 'disponivel'), ('Alugada', 'Alugada')])
    modelo = models.CharField(max_length=100)
    ano_fabricacao = models.IntegerField()

    def __str__(self):
        return f"Bicicleta {self.id} - {self.modelo}"

    def clean(self):
        if self.ano_fabricacao < 1900 or self.ano_fabricacao > timezone.now().year:
            raise ValidationError('Ano de fabricação inválido!')




class Locacao(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('concluida', 'Concluída'),
    ]

    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='locacoes')
    bicicleta = models.ForeignKey('Bicicleta', on_delete=models.CASCADE)
    data_locacao = models.DateTimeField(default=timezone.now)
    data_devolucao = models.DateTimeField(null=True, blank=True)
    pagamento = models.ForeignKey('Pagamento', on_delete=models.SET_NULL, null=True, blank=True)
    data_pagamento = models.DateTimeField(null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')

    VALOR_POR_HORA = 5.00

    def calcular_valor(self):
        """
        Calcula o valor da locação com base na diferença entre data_locacao e data_devolucao.
        """
        if self.data_locacao and self.data_devolucao:
            duracao = self.data_devolucao - self.data_locacao
            horas = duracao.total_seconds() // 3600
            valor_calculado = self.VALOR_POR_HORA * (horas + 1)   
            return round(valor_calculado, 2)
        return 0.00

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para calcular o valor automaticamente antes de salvar.
        """
        if not self.valor and self.data_locacao and self.data_devolucao:
            self.valor = self.calcular_valor()
        super().save(*args, **kwargs)

    def locar_bicicleta(self):
        """
        Marca a bicicleta como alugada.
        """
        if self.bicicleta.status == 'disponivel':
            self.bicicleta.status = 'Alugada'
            self.bicicleta.save()
            self.save()
        else:
            raise ValidationError("Bicicleta não disponível para locação.")

    def devolver_bicicleta(self):
        """
        Marca a bicicleta como disponível e atualiza as informações de devolução.
        """
        if self.bicicleta.status == 'Alugada':
            self.bicicleta.status = 'disponivel'
            self.bicicleta.save()
            self.data_devolucao = timezone.now()
            self.status = 'concluida'
            self.save()
        else:
            raise ValidationError("Bicicleta não está alugada.")

    def realizar_pagamento(self):
        """
        Registra o pagamento da locação.
        """
        if self.pagamento:
            self.data_pagamento = timezone.now()
            self.save()

    def __str__(self):
        return f"Locação {self.id} - {self.usuario.nome} ({self.bicicleta.modelo})"


class Cartao(models.Model):
    BANDEIRAS = [
        ('Visa', 'Visa'),
        ('Mastercard', 'Mastercard'),
        ('American Express', 'American Express'),
        ('Elo', 'Elo'),
        ('Hipercard', 'Hipercard'),
    ]

    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cartoes') 
    numero_cartao = models.CharField(max_length=19, unique=True)   
    validade_cartao = models.CharField(max_length=7)   
    cvv = models.CharField(max_length=3)
    bandeira = models.CharField(max_length=20, choices=BANDEIRAS, default='Visa')

    def __str__(self):
        return f"Cartão {self.bandeira} de {self.usuario.username}"
