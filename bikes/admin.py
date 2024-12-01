from django.contrib import admin
from .models import Bicicleta, Usuario, Locacao, Estacao, Pagamento, Cartao

class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'nome', 'email', 'cpf', 'data_nascimento', 'is_staff', 'is_superuser')
    search_fields = ('username', 'nome', 'email', 'cpf')
    list_filter = ('is_staff', 'is_superuser', 'possui_deficiencia')
    ordering = ('nome',)

class LocacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'bicicleta', 'data_locacao', 'data_devolucao', 'data_pagamento')
    list_filter = ('data_locacao', 'data_devolucao', 'bicicleta__status')
    search_fields = ('usuario__nome', 'bicicleta__modelo')

class BicicletaAdmin(admin.ModelAdmin):
    list_display = ('id', 'modelo', 'ano_fabricacao', 'status', 'estacao')
    list_filter = ('status', 'ano_fabricacao', 'estacao__nome')
    search_fields = ('modelo', 'estacao__nome')

class EstacaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'latitude', 'longitude')
    search_fields = ('nome',)
    ordering = ('nome',)

class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'forma_pagamento', 'get_numero_cartao', 'get_validade_cartao', 'get_bandeira_cartao')
    list_filter = ('forma_pagamento',)
    search_fields = ('usuario__nome', 'cartao__numero_cartao')

     
    def get_numero_cartao(self, obj):
        return obj.cartao.numero_cartao if obj.cartao else 'N/A'
    get_numero_cartao.short_description = 'Número do Cartão'

    def get_validade_cartao(self, obj):
        return obj.cartao.validade_cartao if obj.cartao else 'N/A'
    get_validade_cartao.short_description = 'Validade'

    def get_bandeira_cartao(self, obj):
        return obj.cartao.bandeira if obj.cartao else 'N/A'
    get_bandeira_cartao.short_description = 'Bandeira'

class CartaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'numero_cartao', 'validade_cartao', 'bandeira')
    search_fields = ('usuario__username', 'numero_cartao')

admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Locacao, LocacaoAdmin)
admin.site.register(Bicicleta, BicicletaAdmin)
admin.site.register(Estacao, EstacaoAdmin)
admin.site.register(Pagamento, PagamentoAdmin)
admin.site.register(Cartao, CartaoAdmin)
