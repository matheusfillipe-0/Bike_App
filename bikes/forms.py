from django import forms
from django.contrib.auth import get_user_model
from .models import Usuario 
from django.core.exceptions import ValidationError
from datetime import datetime
from .models import Cartao

User = get_user_model()

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = [
            'nome', 'cpf', 'data_nascimento',
            'possui_deficiencia', 'deficiencia', 'cep','logradouro', 'numero',
            'bairro', 'cidade', 'estado', 'email','username', 'password'
        ]
    
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Senha")
    username = forms.CharField(required=True, label="Nome de Usuário")
    
    def clean_data_nascimento(self):
        """
        Validação para garantir que a data de nascimento seja no passado.
        """
        data_nascimento = self.cleaned_data.get('data_nascimento')

        if data_nascimento is not None and data_nascimento >= datetime.today().date():
            raise ValidationError('A data de nascimento deve ser no passado.')
        return data_nascimento

    def clean(self):
        """
        Validações customizadas para campos relacionados.
        """
        cleaned_data = super().clean()
        possui_deficiencia = cleaned_data.get('possui_deficiencia')
        deficiencia = cleaned_data.get('deficiencia')

        if possui_deficiencia and not deficiencia:
            self.add_error('deficiencia', 'Por favor, descreva a deficiência se você marcou "Possui deficiência".')

        return cleaned_data

    def save(self, commit=True):
        nome = self.cleaned_data['nome']
        cpf = self.cleaned_data.get('cpf')
        email = self.cleaned_data['email']
        data_nascimento = self.cleaned_data['data_nascimento']
        possui_deficiencia = self.cleaned_data['possui_deficiencia']
        deficiencia = self.cleaned_data['deficiencia']
        logradouro = self.cleaned_data['logradouro']
        numero = self.cleaned_data['numero']
        bairro = self.cleaned_data['bairro']
        cidade = self.cleaned_data['cidade']
        estado = self.cleaned_data['estado']
        cep = self.cleaned_data['cep']
        password = self.cleaned_data['password']
        username = self.cleaned_data['username']
         
        user = Usuario(
            username=username,
            nome=nome,
            cpf=cpf,
            email=email,
            data_nascimento=data_nascimento,
            possui_deficiencia=possui_deficiencia,
            deficiencia=deficiencia,
            logradouro=logradouro,
            numero=numero,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            cep=cep
        )
         
        user.set_password(password)
         
        if commit:
            user.save()
        
        return user


class CartaoForm(forms.ModelForm):
    class Meta:
        model = Cartao
        fields = ['numero_cartao', 'validade_cartao', 'cvv', 'bandeira']

    bandeira = forms.ChoiceField(
        choices=Cartao.BANDEIRAS,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Bandeira do Cartão"
    )

    def clean_numero_cartao(self):
        numero_cartao = self.cleaned_data.get('numero_cartao')
        if len(numero_cartao) != 16 or not numero_cartao.isdigit():
            raise forms.ValidationError("Número do cartão deve conter exatamente 16 dígitos.")
        return numero_cartao

    def clean_validade_cartao(self):
        validade = self.cleaned_data.get('validade_cartao')
        if len(validade) != 7 or validade[2] != '/':
            raise forms.ValidationError("Formato de validade inválido. Use MM/AAAA.")
        try:
            validade_parts = validade.split('/')
            if int(validade_parts[0]) not in range(1, 13):
                raise forms.ValidationError("Mês inválido. Use MM/AAAA.")
            validade_date = datetime.strptime(validade, "%m/%Y")
             
            if validade_date <= datetime.now():
                raise forms.ValidationError("A data de validade deve ser no futuro.")
        except:
            raise forms.ValidationError("Formato de validade inválido. Use MM/AAAA.")
        return validade

    def clean_cvv(self):
        cvv = self.cleaned_data.get('cvv')
        if len(cvv) not in [3, 4] or not cvv.isdigit():
            raise forms.ValidationError("O CVV deve conter 3 ou 4 dígitos.")
        return cvv