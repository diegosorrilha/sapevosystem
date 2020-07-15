import logging

from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from core.forms import DecisorForm, NomeProjetoForm, AlternativaForm, CriterioForm
from core.models import Projeto, Decisor, Alternativa, Criterio, AvaliacaoCriterios, AvaliacaoAlternativas, PageView

from services.alternativa_service import AlternativaService
from services.calculo import Calculo
from services.matriz import Matriz

logger = logging.getLogger(__name__)


def index(request):
    template_name = 'index.html'
    projetos = Projeto.objects.all()

    if request.method == "POST":
        nome_projeto_form = NomeProjetoForm(request.POST)
        if nome_projeto_form.is_valid():
            projeto_novo = nome_projeto_form.save()

        return redirect('cadastradecisores', projeto_id=projeto_novo.id)

    else:
        nome_projeto_form = NomeProjetoForm()

    pageview = registra_pageview()

    return render(request, template_name, {
                'nome_projeto_form': nome_projeto_form,
                'projetos': projetos,
                'pageview': pageview})


def metodo(request):
    template_name = 'metodo.html'

    pageview = registra_pageview()

    return render(request, template_name, {
        'pageview': pageview
    })


def projeto(request, projeto_id):
    template_name = 'projeto.html'
    projeto = Projeto.objects.get(id=projeto_id)
    decisores = Decisor.objects.filter(projeto=projeto_id)
    alternativas = Alternativa.objects.filter(projeto=projeto_id)
    criterios = Criterio.objects.filter(projeto=projeto_id)


    return render(request, template_name, {
                'projeto': projeto,
                'decisores': decisores,
                'alternativas': alternativas,
                'criterios': criterios})


def deletarprojeto(request, projeto_id):
    redirect_page = '/'
    params_redirect = ''

    try:
        projeto = Projeto.objects.get(id=projeto_id)
        projeto.delete()
        logger.info('Projeto deletado com sucesso | projeto: {}'.format(projeto))

    except:
        redirect_page = 'resultado'
        params_redirect = projeto_id
        logger.error('Projeto deletado com sucesso | ID: {}'.format(projeto_id))

    return redirect(redirect_page, projeto_id=params_redirect)


def editardados(request):
    nome = request.POST['nome']
    tipo_id = request.POST['tipoId'].split(':') 
    tipo, _id = tipo_id[0], tipo_id[1]
    
    if tipo == 'projeto':
        projeto = Projeto.objects.get(id=_id)
        projeto.nome = nome
        projeto.save()

    elif tipo == 'decisor':
        decisor = Decisor.objects.get(id=_id)
        decisor.nome = nome
        decisor.save()

    elif tipo == 'alternativa':
        alternativa = Alternativa.objects.get(id=_id)
        alternativa.nome = nome
        alternativa.save()

    elif tipo == 'criterio':
        criterio = Criterio.objects.get(id=_id)
        criterio.nome = nome
        criterio.save()

    return HttpResponse(nome)


def cadastradecisores(request, projeto_id):
    projeto = Projeto.objects.get(id=projeto_id)
    template_name = 'cadastra_decisores.html'
    projeto_nome = projeto.nome
    decisores = Decisor.objects.filter(projeto=projeto_id)
    qtd_decisores = len(decisores)

    if request.method == 'POST':
        decisor_form = DecisorForm(request.POST)
        if decisor_form.is_valid():
            decisor_novo = decisor_form.save()
            _inclui_decisor_no_projeto(projeto, decisor_novo)
            decisor_novo.projeto = projeto
            decisor_novo.save()

            logger.info('Projeto: {} | ID: {}'.format(projeto, projeto.id))
            logger.info('Decisor cadastrado: {} | ID {}'.format(decisor_novo, decisor_novo.id))

        return redirect('cadastradecisores', projeto_id=projeto.id)

    else:
        decisor_form = DecisorForm()

    return render(request, template_name, {
                'decisor_form': decisor_form, 
                'decisores': decisores, 
                'projeto_nome': projeto_nome,
                'projeto_id': projeto_id,
                'qtd_decisores': qtd_decisores})


def cadastraalternativas(request, projeto_id):
    projeto = Projeto.objects.get(id=projeto_id)
    template_name = 'cadastra_alternativas.html'
    projeto_nome = projeto.nome
    alternativas = Alternativa.objects.filter(projeto=projeto_id)
    ultima_alternativa = None

    if alternativas:
        ultima_alternativa = alternativas.order_by('-id')[0]

    if request.method == 'POST':
        alternativa_form = AlternativaForm(request.POST)
        if alternativa_form.is_valid():
            if ultima_alternativa:
                codigo_ultima_alternativa = ultima_alternativa.codigo
                codigo = '{}{}'.format(
                    codigo_ultima_alternativa[0],
                    int(codigo_ultima_alternativa[1])+1)
            else:
                codigo = 'a1'

            alternativa_nova = alternativa_form.save()
            alternativa_nova.projeto = projeto
            alternativa_nova.codigo = codigo
            alternativa_nova.save()

            logger.info('Projeto: {} | ID: {}'.format(projeto, projeto.id))
            logger.info('Alternativa cadastrada: {} | ID {}'.format(alternativa_nova, alternativa_nova.id))
        
        return redirect('cadastraalternativas', projeto_id=projeto.id)

    else:
        alternativa_form = AlternativaForm()

    return render(request, template_name, {
                'alternativa_form': alternativa_form,
                'alternativas': alternativas,
                'projeto_nome': projeto_nome,
                'projeto_id': projeto_id})


def cadastracriterios(request, projeto_id):
    projeto = Projeto.objects.get(id=projeto_id)
    template_name = 'cadastra_criterios.html'
    projeto_nome = projeto.nome
    criterios = Criterio.objects.filter(projeto=projeto_id)
    ultimo_criterio = None

    if criterios:
        ultimo_criterio = criterios.order_by('-id')[0]

    if request.method == 'POST':
        criterio_form = CriterioForm(request.POST)
        if criterio_form.is_valid():
            if ultimo_criterio:
                codigo_ultimo_criterio = ultimo_criterio.codigo
                codigo = '{}{}'.format(
                    codigo_ultimo_criterio[0], 
                    int(codigo_ultimo_criterio[1])+1)
            else:
                codigo = 'c1'

            criterio_novo = criterio_form.save()
            criterio_novo.projeto = projeto
            criterio_novo.codigo = codigo
            criterio_novo.save()

            logger.info('Projeto: {} | ID: {}'.format(projeto, projeto.id))
            logger.info('Critério cadastrado: {} | ID {}'.format(criterio_novo, criterio_novo.id))

            return redirect('cadastracriterios', projeto_id=projeto.id)
    
    else:
        criterio_form = CriterioForm()

    return render(request, template_name, {
                'criterio_form': criterio_form,
                'criterios': criterios,
                'projeto_nome': projeto_nome,
                'projeto_id': projeto_id,
    })


def avaliarcriterios(request, projeto_id):
    '''
    View para avaliar os critérios cadastrados.    
    ''' 
    template_name = 'avaliar_criterios.html'
    projeto_id = projeto_id
    projeto = Projeto.objects.get(id=projeto_id)
    decisores = list(Decisor.objects.filter(projeto=projeto_id, avaliou_criterios=False).values_list('id', 'nome'))
    criterios_cod = Criterio.objects.filter(projeto=projeto_id).values_list('codigo', flat=True)

    if not decisores:
        return redirect('avaliaralternativas', projeto_id)

    combinacoes_criterios = _gerar_combinacoes_criterios(criterios_cod)
    
    criterios_combinados = []
    for i in combinacoes_criterios:
        cod_crit1 = i[0]
        cod_crit2 = i[1]

        nome_criterio1 = Criterio.objects.get(projeto=projeto_id, codigo=cod_crit1).nome
        nome_criterio2 = Criterio.objects.get(projeto=projeto_id, codigo=cod_crit2).nome

        criterios_combinados.append(
            (nome_criterio1, nome_criterio2, i[0], i[1])
        )

    if request.method == 'POST':
        decisor_id = request.POST['decisor_id']
        campos = request.POST.keys()
        decisor = Decisor.objects.get(id=decisor_id)

        logger.info('Projeto: {} | ID: {}'.format(projeto, projeto.id))

        for campo in campos:
            if campo.startswith('c') and not campo.startswith('csrf'):
                avaliacao = AvaliacaoCriterios(
                    projeto=projeto,
                    decisor=decisor,
                    criterios=campo,
                    valor=request.POST[campo]
                )
                avaliacao.save()

                logger.info('Avaliação de critério cadastrada: {} | ID {}'.format(avaliacao, avaliacao.id))

        decisor.avaliou_criterios = True
        decisor.save()

        logger.info('Decisor atualizado: {} | ID {}'.format(decisor, decisor.id))

        return redirect('avaliarcriterios', projeto_id)

    return render(request, template_name, {
                'decisores': decisores,
                'criterios_combinados': criterios_combinados,
                'projeto_nome': projeto.nome,
                })
     

def avaliaralternativas(request, projeto_id):
    '''
    View para avaliar as alternativas cadastradas.
    '''
    template_name = 'avaliar_alternativas.html'
    projeto_id = projeto_id
    projeto = Projeto.objects.get(id=projeto_id)
    decisores = list(Decisor.objects.filter(projeto=projeto_id, avaliou_alternativas=False).values_list('id', 'nome'))
    alternativas_id = Alternativa.objects.filter(projeto=projeto_id).values_list('codigo', flat=True)
    criterios = Criterio.objects.filter(projeto=projeto_id)

    if not decisores:
        return redirect('resultado', projeto_id)

    combinacoes_alternativas = _gerar_combinacoes_criterios(alternativas_id)

    alternativas_combinadas = []
    for i in combinacoes_alternativas:
        cod_alt1 = i[0]
        cod_alt2 = i[1]

        nome_alternativa1 = Alternativa.objects.get(projeto=projeto_id, codigo=cod_alt1).nome
        nome_alternativa2 = Alternativa.objects.get(projeto=projeto_id, codigo=cod_alt2).nome

        alternativas_combinadas.append(
            (nome_alternativa1, nome_alternativa2, i[0], i[1])
        )

    if request.method == 'POST':
        decisor_id = request.POST['decisor_id']
        campos = request.POST.keys()
        decisor = Decisor.objects.get(id=decisor_id)

        logger.info('Projeto: {} | ID: {}'.format(projeto, projeto.id))

        for campo in campos:
            # if campo.startswith('c') and not campo.startswith('csrf'):
                # criterio_id = campo[1]
            if not campo.startswith('csrf') and not campo.startswith('d'):
                if campo.split('-->')[1].startswith('c'):
                    criterio_id = campo.split('-->')[0]

                    #### PROBLEMA ESTÁ AQUI
                    # print('CAMPO',campo)
                    # print('campo1', campo[1])
                    # print('criterio_id', criterio_id)
                    criterio = Criterio.objects.get(id=criterio_id)
                    # print('chegou aqui?')
                    avaliacao = AvaliacaoAlternativas(
                        projeto=projeto,
                        decisor=decisor,
                        criterio=criterio,
                        alternativas=campo,
                        valor=request.POST[campo],
                    )
                    avaliacao.save()

                    logger.info('Avaliação de alternativa cadastrada: {} | ID {}'.format(avaliacao, avaliacao.id))
                

        decisor.avaliou_alternativas = True
        decisor.save()
        projeto.avaliado = True
        projeto.save()
        logger.info('Decisor atualizado: {} | ID {}'.format(decisor, decisor.id))
        logger.info('Projeto atualizado: {} | ID {}'.format(projeto, projeto.id))

        return redirect('avaliaralternativas', projeto_id)

    return render(request, template_name, {
                'decisores': decisores,
                'alternativas_combinadas': alternativas_combinadas,
                'criterios': criterios,
                'projeto_nome': projeto.nome,
                })


def _gerar_matrizes_criterios(decisores, qtd_criterios, projeto_id):
    matrizes = []
    for decisor in decisores:
        criterios_decisor = AvaliacaoCriterios.objects.filter(projeto=projeto_id, decisor=decisor.id)
        matriz = Matriz().gerar_matriz(qtd_criterios, criterios_decisor)
        matrizes.append(matriz)

    logger.info('Matrizes geradas: {}'.format(matrizes))
    return matrizes

# Calculo
def _calcular_peso_criterios(matrizes, criterios):
    pesos_decisores = []
    for matriz in matrizes:
        peso_matriz = _normalizar(matriz)
        pesos_decisores.append(peso_matriz)

    logger.info('Pesos decisores com matrizes normalizadas: {}'.format(pesos_decisores))

    # calcular o peso final
    peso_final = Calculo().get_peso_criterios(pesos_decisores)
    logger.info('Pesos final de critérios calculado: {}'.format(peso_final))

    # cria tupla de criterio e peso para renderizar
    pesos_criterios = []
    pos_peso = 0
    peso_final_qt = len(peso_final)

    while pos_peso < peso_final_qt:
        for criterio in criterios:
            pesos_criterios.append((criterio.nome, peso_final[pos_peso]))
            pos_peso += 1

    logger.info('Pesos por criterios: {}'.format(pesos_criterios))
    return pesos_criterios, peso_final


def _gerar_matriz_alternativas(
        decisores,
        criterios,
        qtd_criterios,
        projeto_id,
        qtd_alternativas
    ):
    # gera dicionario de matrizes
    d_matrizes = {}
    for decisor in decisores:
        k = 'D{}'.format(decisor.id)
        d_matrizes[k] = []

    # gera dicionario de avaliacoes
    d_avaliacoes = {}
    for decisor in decisores:
        k = 'D{}'.format(decisor.id)
        d_avaliacoes[k] = []
        for i in range(qtd_criterios):
            d_avaliacoes[k].append(list())

    lista_criterios = []
    for c in criterios:
        lista_criterios.append(c.codigo)

    logger.info('Lista de criterios: {}'.format(lista_criterios))

    # a partir daqui
    avaliacoes_alt = AvaliacaoAlternativas.objects.filter(projeto=projeto_id).order_by('alternativas')
    logger.info('Avaliacao Alternativas : {}'.format(avaliacoes_alt))

    for i in avaliacoes_alt:
        k = 'D{}'.format(i.decisor.id)
        indice = lista_criterios.index(i.criterio.codigo)
        d_avaliacoes[k][indice].append(i.valor)

    logger.info('Avaliações de alternativas: {}'.format(d_avaliacoes))

    # gera matrizes ################
    matrizes = AlternativaService().gerar_matrizes(d_matrizes, d_avaliacoes, qtd_alternativas)

    return matrizes

def _calcular_resultado_alternativas(
        matrizes,
        qtd_criterios,
        peso_final,
        projeto_id
        ):
    resultado_um = AlternativaService().calcular_resultado(matrizes, qtd_criterios, peso_final)

    alternativas = Alternativa.objects.filter(projeto=projeto_id)

    resultado = []
    count = 0

    while count < len(alternativas):
        resultado.append(
            (alternativas[count], resultado_um[count])
        )
        count += 1

    resultado.sort(key=lambda x: x[1], reverse=True)

    logger.info('Resultado: {}'.format(resultado))

    return resultado


def resultado(request, projeto_id):
    template_name = 'resultado.html'

    projeto_id = projeto_id
    projeto = Projeto.objects.get(id=projeto_id)
    qtd_criterios = Criterio.objects.filter(projeto=projeto_id).count()
    qtd_alternativas = Alternativa.objects.filter(projeto=projeto_id).count()
    decisores = projeto.decisores.all()
    criterios = Criterio.objects.filter(projeto=projeto_id)

    logger.info('Projeto: {} | ID: {}'.format(projeto, projeto.id))

    #### Criterios ####
    matrizes = _gerar_matrizes_criterios(decisores, qtd_criterios, projeto_id)

    #### Calcular pesos dos criterios #### # Calculo
    pesos_criterios, peso_final = _calcular_peso_criterios(matrizes, criterios)

    #### Alternativas ####
    d_matrizes = _gerar_matriz_alternativas(  # d_matrizes > matrizes_alt
        decisores,
        criterios,
        qtd_criterios,
        projeto_id,
        qtd_alternativas
    )

    resultado = _calcular_resultado_alternativas(  # Calculo
        d_matrizes,
        qtd_criterios,
        peso_final,
        projeto_id
    )

    return render(request, template_name, {
        'projeto_nome': projeto.nome,
        'projeto_id': projeto.id,
        'resultado': resultado,
        'pesos_criterios': pesos_criterios,
        })


#################################
######## aux functions   ########
#################################
# TODO: colocar em arquivo separado

def _inclui_decisor_no_projeto(projeto, decisor):
    projeto.decisores.add(decisor)
    return

# Calculo._normalizar
def _normalizar(lista_elementos):
    lista_final_normalizada = []
    lista_dos_somados = []
    lista_normalizada = []
    lista_sem_zero = []
    for elemento in lista_elementos:
        soma = sum(elemento)
        lista_dos_somados.append(soma)
    
    for elemento_da_soma in lista_dos_somados:
        maior , menor = max(lista_dos_somados), min(lista_dos_somados)
        if maior == menor:
            regular = 0
        else:
            regular = ((elemento_da_soma - menor)/(maior - menor))
        lista_normalizada.append(regular)
    
    for i in lista_normalizada:
        if i > 0:
            lista_sem_zero.append(i)

    for elemento_normalizado in lista_normalizada:
        if elemento_normalizado > 0:
            lista_final_normalizada.append(elemento_normalizado)
        else:
            menor_zero = min(lista_sem_zero)
            lista_final_normalizada.append(menor_zero*0.01)

    return lista_final_normalizada


# Matriz._gerar_combinacoes_criterios
def _gerar_combinacoes_criterios(criterios):
    '''
    Funcao que gera combinacoes de criterios e alternativas
    de acordo os criterios e alternativas cadastrados

    Recebe uma lista com os codigos dos criterios (Queryset)
    [c1, c2, c3, c4]

    Retorna uma lista de tuplas
    [(c1, c2), (c1,c3) ('c1', 'c4')]

    -------

    Recebe uma lista com os codigos das alternativas (Queryset)
    [a1, a2, a3, a4]

    Retorna uma lista de tuplas
    [(a1, a2), (a1,a3) ('a1', 'a4')]
    '''
    from itertools import product

    criterios_keys = criterios
    genComb = product(criterios_keys, repeat=2)

    combinacoes = []
    for subset in genComb:
        l = list(subset)
        l.reverse()
        subset_reversed = tuple(l)

        if not subset[0] == subset[1]:
            if subset not in combinacoes  and subset_reversed not in combinacoes:
                combinacoes.append(subset)

    return combinacoes

# Calculo
def _separa_alternativas(criterio, lista_elementos, idx):
    num_el = len(lista_elementos[0])
    lista_separada = []
    
    if idx < num_el:
        for item in lista_elementos:
            lista_separada.append(item[idx])
    return lista_separada


# Calculo
def _separa_primeiros_elementos(lista_elementos, idx):
    
    lista_separada = []
    lista_separada = lista_elementos[idx]
        
    return lista_separada

# Calculo
def _multiplicar_pelo_peso(lista_primeiros_elementos ,lista_pesos):
    lista_multi = []
    for numint, peso in enumerate(lista_pesos):
  
        multi = peso * lista_primeiros_elementos[numint]
        lista_multi.append(multi)

    return lista_multi

def registra_pageview():
    pageviews = PageView.objects.all()

    if pageviews:
        pageview = pageviews.get(id=1)
        pageview.views += 1
    else:
        pageview = PageView()
        pageview.views = 1
    pageview.save()

    return pageview.views
