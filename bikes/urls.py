from django.urls import path
from . import views

urlpatterns = [
    # Autenticação e Cadastro
    path('login/', views.login_view, name='login'),
    path('cadastro/', views.cadastro_usuario, name='cadastro_usuario'),
    path('logout/', views.logout_view, name='logout'),  # URL para "Sair"

    # Cadastro de Pagamento
    path('cadastro-pagamento/', views.cadastro_cartao, name='cadastro_cartao'),
    path('cadastro-cartao/<int:bicicleta_id>/', views.cadastro_novo_cartao, name='cadastro_novo_cartao'),

    # Páginas Principais
    path('home/', views.home, name='home'),
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),  # URL para "Perfil"
    path('configuracoes/', views.configuracoes_usuario, name='configuracoes_usuario'),  # URL para "Configurações"
    path('historico/', views.historico_locacoes, name='historico_locacoes'),
    path('logout/', views.logout_view, name='logout'),
    path('modificar-nome/', views.modificar_nome, name='modificar_nome'),
    path('atualizar_nome/', views.atualizar_nome, name='atualizar_nome'), 
    path('atualizar_email/', views.atualizar_email, name='atualizar_email'), 
    path('modificar_email/', views.modificar_email, name='modificar_email'),
    path('alterar-senha/', views.alterar_senha, name='alterar_senha'),
     
 
    path('estacao/<int:estacao_id>/', views.detalhes_estacao, name='detalhes_estacao'),
    path('reserva-bicicleta/<int:bicicleta_id>/', views.reserva_bicicleta, name='reserva_bicicleta'),
    path('confirmacao-reserva/<int:bicicleta_id>/', views.confirmacao_reserva, name='confirmacao_reserva'),
    path('home_locacao/<int:id_bicicleta>/', views.home_locacao, name='home_locacao'),

]