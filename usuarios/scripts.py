from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from .forms import FornecedorForms, TipoAgregadoForms, AgregadoForms, TracoForms, TracoAgregadoForms
from .models import Fornecedor, TipoAgregado, Agregado, Traco, TracoAgregado
from django.utils import timezone
from django.db.models import F
from datetime import datetime
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.contrib import messages
import math


def GetInformacoesAgregados(agregados_traco, tipos_agregado):
    porcentagem_agregados = []
    value = ''
    for tipo_agregado in tipos_agregado:
        for agregado_traco in agregados_traco:
            if agregado_traco.agregado.fk_tipo_agregado_id == tipo_agregado:
                value = agregado_traco.porcentagem
                break
        porcentagem_agregados.append(value)

    informacoes_agregados = []
    for index, tipo_agregado in enumerate(tipos_agregado):

        agregados_info = []
        for agregado in tipo_agregado.agregados_relacionados():
            selected = ''
            for agregado_traco in agregados_traco:
                if agregado.id == agregado_traco.agregado_id:
                    selected = 'selected'
            print(agregados_traco)
            agregados_info.append({
                'nome': agregado.nome,
                'id': agregado.id,
                'selected': selected
            })
        info = {
            'tipo_agregado': tipo_agregado.nome,
            'tipo_agregado_id': tipo_agregado.id,
            'porcentagem': str(porcentagem_agregados[index]),
            'agregados': agregados_info
        }
        informacoes_agregados.append(info)

    return informacoes_agregados


def InsertTraco(request, context, agregados, porcentagem_agregados, render_file):
    porcentagem_total = context['form'].cleaned_data['porcentagem_agua']
    for index, agregado_id in enumerate(agregados):
        if agregado_id != '' and porcentagem_agregados[index] != '':
            porcentagem_total = porcentagem_total + float(porcentagem_agregados[index])

    if round(porcentagem_total) != 100:
        context['errors'] = {
                'code': 1,
                'message': f"A soma das porcentagens é diferente de 100%! A soma atual é {porcentagem_total}%"
            }
        return render(request, render_file, context)

    traco = context['form'].save()

    TracoAgregado.objects.filter(traco=traco).delete()
    # Processar e salvar as porcentagens dos agregados
    for index, agregado_id in enumerate(agregados):
        if agregado_id != '':
            agregado = Agregado.objects.get(id=agregado_id)

            TracoAgregado.objects.create(traco=traco, agregado=agregado,
                                         porcentagem=porcentagem_agregados[index])
    return redirect('traco')


def CalcularTraco(volume_traco, traco, multiplicador, unidade_medida):
    agregados_traco = TracoAgregado.objects.filter(traco=traco)

    quantidade_agua_total = round(volume_traco*multiplicador*(traco.porcentagem_agua/100), 2)
    quantidade_agua_necessaria = quantidade_agua_total

    peso_final = 0
    agregados_info = []

    for agregado_traco in agregados_traco:
        massa_especifica = agregado_traco.agregado.massa_especifica
        porcentagem = agregado_traco.porcentagem

        peso_sem_umidade = volume_traco*massa_especifica*multiplicador*(porcentagem/100)
        peso_com_umidade = (100*peso_sem_umidade)/(100-agregado_traco.agregado.umidade)

        quantidade_agua_necessaria = quantidade_agua_necessaria - peso_com_umidade*agregado_traco.agregado.umidade/100
        peso_final = peso_final + peso_com_umidade

        agregados_info.append({
            'nome': agregado_traco.agregado.nome,
            'id': agregado_traco.agregado.id,
            'tipo_agregado': agregado_traco.agregado.fk_tipo_agregado_id.nome,
            'quantidade': round(peso_com_umidade, 2),
            'unidade_medida': 'Kg'
        })

    peso_final = peso_final + quantidade_agua_necessaria
    agregados_info.append({
        'nome': 'Água',
        'id': '0',
        'tipo_agregado': 'Água',
        'quantidade': round(quantidade_agua_necessaria, 2),
        'unidade_medida': 'Litros'
    })

    calculo_object = {
        'traco': {
            'nome': traco.nome,
            'id': traco.id,
            'descricao': traco.descricao
        },
        'volume_traco': volume_traco,
        'unidade_medida': unidade_medida,
        "peso_final": round(peso_final, 2),
        'agregados': agregados_info
    }

    return calculo_object


def get_last_agregado(agregado_id):
    agregados = Agregado.objects.filter(id=agregado_id)
    return ''


def resolve_unidade_medida(unidade_medida):
    if unidade_medida == 'm3':
        multiplicador = 1000
        unidade_medida_display = 'Metro(s) cúbico(s) (m³)'
    elif unidade_medida == 'l':
        multiplicador = 1
        unidade_medida_display = 'Litro(s) (l)'
    else:
        multiplicador = 'ERRO AO RESOLVER resolve_unidade_medida()'
        unidade_medida_display = 'ERRO AO RESOLVER resolve_unidade_medida()'

    return multiplicador, unidade_medida_display


def get_user_group(request):
    return request.user.groups.all()[0].name
