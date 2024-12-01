from django.shortcuts import render, redirect
from .forms import UsuarioForm
from django.contrib import messages
from .models import Usuario 
from django.contrib.auth import authenticate, login
from .models import Estacao
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
import json
from .models import Bicicleta
from django.utils import timezone
from .models import Locacao, Bicicleta, Pagamento, Usuario
from .forms import CartaoForm
from .models import Bicicleta, Cartao 
import logging
from django.contrib.auth import logout
from django.core.exceptions import ValidationError
from django.core.validators import validate_email 
from datetime import timedelta
from django.utils.timezone import now
import json


logger = logging.getLogger(__name__)

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        usuario = authenticate(request, username=username, password=password)
        
        if usuario is not None:
            if usuario.is_superuser:
                return redirect('/admin/')   
            
            login(request, usuario)  
            return redirect('home')  
        else:
            messages.error(request, 'Usuário ou senha incorretos.')   
    
    return render(request, 'bikes/login.html')  
  


@login_required
def home(request):
    estacoes = Estacao.objects.all()
     
    locacao_ativa = Locacao.objects.filter(
        usuario=request.user,
        data_locacao__lte=now(),  
        data_devolucao__gte=now()   
    ).exists()
 
    estacoes_json = json.dumps([{
        'id': estacao.id,
        'nome': estacao.nome,
        'latitude': estacao.latitude,
        'longitude': estacao.longitude
    } for estacao in estacoes])

    # Renderiza o template com as informações
    return render(request, 'bikes/home.html', {
        'estacoes_json': estacoes_json,
        'locacao_ativa': locacao_ativa   
    })
 
    
    
@login_required
def detalhes_estacao(request, estacao_id):
    estacao = get_object_or_404(Estacao, id=estacao_id)
    bicicletas = estacao.bicicletas.all()   
    return render(request, 'bikes/detalhes_estacao.html', {
        'estacao': estacao,
        'bicicletas': bicicletas
    })
 
 
 
def cadastro_cartao(request):
    if request.method == 'POST':
        form = CartaoForm(request.POST)

        if form.is_valid():
            
            usuario_id = request.session.get('usuario_id')
            if not usuario_id:
                messages.error(request, "Usuário não autenticado. Por favor, refaça o cadastro.")
                return redirect('cadastro_usuario')

            
            usuario = Usuario.objects.get(id=usuario_id)

            # Cria o cartão associado ao usuário
            cartao = form.save(commit=False)
            cartao.usuario = usuario
            cartao.save()

            messages.success(request, "Usuário cadastrado com sucesso !")
            return redirect('login')  
    else:
        form = CartaoForm()

    return render(request, 'bikes/cadastro_cartao.html', {'form': form})


def cadastro_usuario(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)

        if form.is_valid():
            cpf = form.cleaned_data.get('cpf')
            email = form.cleaned_data.get('email')
 
            if Usuario.objects.filter(cpf=cpf).exists():
                messages.error(request, "Este CPF já está cadastrado.")
            elif Usuario.objects.filter(email=email).exists():
                messages.error(request, "Este e-mail já está cadastrado.")
            else:
                
                usuario = form.save()
                
                 
                request.session['usuario_id'] = usuario.id  

                
                return redirect('cadastro_cartao')
    else:
        form = UsuarioForm()

    return render(request, 'bikes/cadastro_usuario.html', {'form': form})
 

@login_required
def reserva_bicicleta(request, bicicleta_id):
    bicicleta = get_object_or_404(Bicicleta, id=bicicleta_id)

     
    if bicicleta.status != 'disponivel':  
        messages.error(request, f'A bicicleta {bicicleta.modelo} não está disponível para locação.')
        return redirect('detalhes_estacao', estacao_id=bicicleta.estacao.id)

    if request.method == 'POST':
        # Captura a forma de pagamento (cartão cadastrado ou novo cartão)
        forma_pagamento = request.POST.get('pagamento')
        cartao_id = request.POST.get('cartao')   
        
        # Verifica se foi informado uma forma de pagamento
        if not forma_pagamento:
            messages.error(request, "A forma de pagamento é obrigatória.")
            return redirect('reserva_bicicleta', bicicleta_id=bicicleta.id)

        if forma_pagamento == 'cartao_cadastrado':
            # Verifica se um cartão foi escolhido
            if not cartao_id:
                messages.error(request, "Você deve selecionar um cartão cadastrado.")
                return redirect('reserva_bicicleta', bicicleta_id=bicicleta.id)
            
            try:
                # Tenta capturar o cartão a partir do ID
                cartao = Cartao.objects.get(id=cartao_id, usuario=request.user)
            except Cartao.DoesNotExist:
                messages.error(request, "Cartão cadastrado inválido.")
                return redirect('reserva_bicicleta', bicicleta_id=bicicleta.id)

            # Criação do pagamento com o cartão selecionado
            pagamento = Pagamento.objects.create(
                usuario=request.user,
                forma_pagamento=Pagamento.CARTAO,
                cartao=cartao,
            )

        elif forma_pagamento == 'novo_cartao':
             
            return redirect('cadastro_novo_cartao', bicicleta_id=bicicleta.id)
        else:
            messages.error(request, "Forma de pagamento inválida.")
            return redirect('reserva_bicicleta', bicicleta_id=bicicleta.id)

        # A data de retirada é automaticamente a data e hora do momento
        data_retirada = timezone.now()

        try:
             
            locacao = Locacao.objects.create(
                usuario=request.user,
                bicicleta=bicicleta,
                data_locacao=data_retirada,  # A data de retirada (hora atual)
                pagamento=pagamento,   
                valor=None  # O valor será preenchido depois
            )

            print(f"Locação criada com pagamento: {locacao.pagamento}")  # Verifica se o pagamento foi associado corretamente

            # Processo da locação
            locacao.locar_bicicleta()  # Processa a locação
            bicicleta.save()  # Salva a bicicleta após a locação

            messages.success(request, f'Bicicleta {bicicleta.modelo} reservada com sucesso!')
            return redirect('confirmacao_reserva', bicicleta_id=bicicleta.id)

        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao realizar a reserva: {str(e)}')
            return redirect('reserva_bicicleta', bicicleta_id=bicicleta.id)

    else:
        # Passa os cartões do usuário para o template, caso o método seja GET
        return render(request, 'bikes/reserva_bicicleta.html', {
            'bicicleta': bicicleta,
            'cartoes': request.user.cartoes.all(),  # Passa os cartões cadastrados do usuário para o template
        })





@login_required
def cadastro_novo_cartao(request, bicicleta_id=None):
    bicicleta = None
 
 
    if bicicleta_id:
        bicicleta = get_object_or_404(Bicicleta, id=bicicleta_id)
 
    if Cartao.objects.filter(usuario=request.user).exists():
        messages.info(request, 'Você já possui um cartão cadastrado.')

    if request.method == 'POST':
        form = CartaoForm(request.POST)
        if form.is_valid():
            cartao = form.save(commit=False)
            cartao.usuario = request.user
            cartao.save()
 
            if bicicleta:
                return redirect('reserva_bicicleta', bicicleta_id=bicicleta.id)  
                

    else:
        form = CartaoForm()

    return render(request, 'bikes/cadastro_novo_cartao.html', {'form': form, 'bicicleta': bicicleta})


@login_required
def confirmacao_reserva(request, bicicleta_id):
    # Recupera a bicicleta reservada com base no ID fornecido
    bicicleta = get_object_or_404(Bicicleta, id=bicicleta_id)
    
    # Verifica se existe uma locação associada à bicicleta e ao usuário autenticado
    locacao = Locacao.objects.filter(bicicleta=bicicleta, usuario=request.user).first()

    if locacao:
        # A locação foi encontrada, passamos os dados para o template
        return render(request, 'bikes/confirmacao_reserva.html', {
            'bicicleta': bicicleta,
            'locacao': locacao,  # Dados da locação
            'data_retirada': locacao.data_locacao,
            'data_devolucao': locacao.data_devolucao,
            'pagamento': locacao.pagamento,
            
        })
    else:
        # Se não houver locação, redireciona para outra página com uma mensagem de erro
        messages.error(request, 'Não foi possível encontrar a locação para essa bicicleta.')
        return redirect('home')  # Ou qualquer outra página de sua escolha


@login_required
def historico_locacoes(request):
    locacoes = Locacao.objects.filter(usuario=request.user).order_by('-data_locacao')
    return render(request, 'bikes/historico.html', {'locacoes': locacoes})
 
 
@login_required
def perfil_usuario(request):
    usuario = request.user  # Recupera o usuário logado
    cartao = usuario.cartoes.first()  # Supondo que o usuário tenha pelo menos um cartão

    # Criar uma variável com os primeiros 6 dígitos do número do cartão
    if cartao:
        cartao_parcial = cartao.numero_cartao[:6]
    else:
        cartao_parcial = None

    return render(request, 'bikes/perfil.html', {
        'usuario': usuario,
        'cartao_parcial': cartao_parcial  # Passando os 6 primeiros dígitos do cartão
    })


@login_required
def logout_view(request):
    logout(request) 
    return redirect('login')  


@login_required
def configuracoes_usuario(request):
    usuario = request.user
    return render(request, 'bikes/configuracoes.html', {'usuario': usuario})


@login_required
def modificar_nome(request):
    return render(request, 'bikes/modificar_nome.html')


@login_required
def modificar_email(request):
    return render(request, 'bikes/modificar_email.html')


@login_required
def atualizar_nome(request):
    if request.method == 'POST':
        novo_nome = request.POST.get('novo_nome')
        if novo_nome:
            # Recupera o usuário autenticado
            user = request.user
            
            
            try:
                usuario = Usuario.objects.get(id=user.id)
                # Atualizando o nome no modelo Usuario
                usuario.nome = novo_nome
                usuario.save()  # Salvando as alterações no banco de dados
                messages.success(request, 'Nome atualizado com sucesso!')
            except Usuario.DoesNotExist:
                messages.error(request, 'Usuário não encontrado.')

            return redirect('home')
        else:
            messages.error(request, 'O nome não pode estar vazio.')

    return render(request, 'bikes/configuracoes.html')
 
 
@login_required
def atualizar_email(request):
    if request.method == 'POST':
        novo_email = request.POST.get('email')

        # Validação do formato de e-mail
        if not novo_email:
            messages.error(request, "O campo de e-mail não pode estar vazio.")
            return redirect('home')

        try:
            validate_email(novo_email)  # Valida o formato do e-mail
        except ValidationError:
            messages.error(request, "Formato de e-mail inválido.")
            return redirect('home')

        # Verificar se o e-mail já está sendo usado por outro usuário
        if request.user.email != novo_email and request.user.__class__.objects.filter(email=novo_email).exists():
            messages.error(request, "Este e-mail já está em uso por outro usuário.")
            return redirect('home')

         
        try:
            usuario = Usuario.objects.get(id=request.user.id)  
            usuario.email = novo_email
            usuario.save()
        except Usuario.DoesNotExist:
            messages.error(request, "Usuário não encontrado.")
            return redirect('home')
 
        request.user.email = novo_email
        request.user.save()

        messages.success(request, "E-mail atualizado com sucesso!")
        return redirect('home')

    return render(request, 'bikes/configuracoes.html')



@login_required
def alterar_senha(request):
    if request.method == 'POST':
        senha_atual = request.POST.get('senha_atual', '').strip()
        nova_senha = request.POST.get('nova_senha', '').strip()
        confirmar_senha = request.POST.get('confirmar_senha', '').strip()

        # Verificar se todos os campos foram preenchidos
        if not senha_atual or not nova_senha or not confirmar_senha:
            messages.error(request, "Todos os campos precisam ser preenchidos.")
            return redirect('alterar_senha')

        # Verificar se a senha atual está correta
        if not request.user.check_password(senha_atual):
            messages.error(request, "Senha atual incorreta.")
            return redirect('alterar_senha')

        # Verificar se as novas senhas coincidem
        if nova_senha != confirmar_senha:
            messages.error(request, "As novas senhas não coincidem.")
            return redirect('alterar_senha')

        # Atualizar a senha
        user = request.user
        user.set_password(nova_senha)
        user.save()

        messages.success(request, "Senha alterada com sucesso!")
        return redirect('login')

    return render(request, 'bikes/alterar_senha.html')
 

@login_required
def home_locacao(request, id_bicicleta):
    bicicleta = Bicicleta.objects.get(id=id_bicicleta)
    
    # Buscar a locação da bicicleta
    locacao = Locacao.objects.filter(bicicleta=bicicleta, status='pendente').first()
    
     
    
    # Obter a lista de estações de devolução
    estacoes = Estacao.objects.all()
    
    if locacao:
        data_locacao = locacao.data_locacao
        tempo_locacao = timezone.now() - locacao.data_locacao   
        
        # Definições de preços
        valor_fixo = 5.00  
        valor_adicional = 2.50 
        
        # Calculando o valor total
        if tempo_locacao <= timedelta(hours=1):
            valor_total = valor_fixo   
        else:
             
            tempo_adicional = tempo_locacao - timedelta(hours=1)
            minutos_adicionais = tempo_adicional.total_seconds() / 60   
            
             
            blocos_30min, restante = divmod(minutos_adicionais, 30)
            
             
            if restante > 0:
                blocos_30min += 1
            
            # Calculando o valor adicional com base nos blocos de 30 minutos
            valor_total = valor_fixo + (blocos_30min * valor_adicional)

    else:
        data_locacao = "Não há locação ativa para esta bicicleta."
        valor_total = 0
    
    if request.method == 'POST':
        try:
             
            locacao.devolver_bicicleta()   
            locacao.valor_total = valor_total  
            locacao.data_devolucao = timezone.now() 
            locacao.realizar_pagamento()   
            
             
            return redirect('home')  
            
        except ValidationError as e:
            
            return render(request, 'bikes/home_locacao.html', {
                'bicicleta': bicicleta,
                'data_locacao': data_locacao,
                'estacoes': estacoes,
                'erro': str(e)
            })
     
     
    return render(request, 'bikes/home_locacao.html', {
        'bicicleta': bicicleta,
        'data_locacao': data_locacao,
        'valor_total': valor_total,
        'estacoes': estacoes,
    })
     