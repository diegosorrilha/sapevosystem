from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from core.forms import DecisorForm, NomeProjetoForm, AlternativaForm, CriterioForm
from core.models import Projeto, Decisor, Alternativa, Criterio, AvaliacaoCriterios, AvaliacaoAlternativa

# aux functions
def _inclui_decisor_no_projeto(projeto, decisor):
    projeto.decisores.add(decisor)
    return


def index(request):
    """ 
    1 - cadastrar somente nome do projeto e redirecionar para cadastrar decisores - OK
    2 - cadastrar decisores - OK
    3 - atualizar cadastro do projeto com decisores - OK
    4 - cadastra Alternativas - OK
    5 - cadastra Criterios - OK
    6 - avalia Critérios - OK
    7 - avalia Alternativas
    8 - coloca resultado final da avaliação no projeto
    """
    template_name = 'index.html'
    projetos = Projeto.objects.all()

    if request.method == "POST":
        nome_projeto_form = NomeProjetoForm(request.POST)
        if nome_projeto_form.is_valid():
            projeto_novo = nome_projeto_form.save()

        return redirect('cadastradecisores', projeto_id=projeto_novo.id)

    else:
        nome_projeto_form = NomeProjetoForm()

    return render(request, template_name, {
                'nome_projeto_form': nome_projeto_form,
                'projetos': projetos})


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


def cadastradecisores(request, projeto_id):
    projeto = Projeto.objects.get(id=projeto_id)
    template_name = 'cadastra_decisores.html'
    projeto_nome = projeto.nome
    decisores = Decisor.objects.filter(projeto=projeto_id)

    if request.method == 'POST':
        decisor_form = DecisorForm(request.POST)
        if decisor_form.is_valid():
            decisor_novo = decisor_form.save()
            _inclui_decisor_no_projeto(projeto, decisor_novo)
            decisor_novo.projeto = projeto
            decisor_novo.save()

    else:
        decisor_form = DecisorForm()

    return render(request, template_name, {
                'decisor_form': decisor_form, 
                'decisores': decisores, 
                'projeto_nome': projeto_nome,
                'projeto_id': projeto_id})


def cadastraalternativas(request, projeto_id):
    projeto = Projeto.objects.get(id=projeto_id)
    template_name = 'cadastra_alternativas.html'
    projeto_nome = projeto.nome
    alternativas = Alternativa.objects.filter(projeto=projeto_id)

    if request.method == 'POST':
        alternativa_form = AlternativaForm(request.POST)
        if alternativa_form.is_valid():
            alternativa_nova = alternativa_form.save()
            alternativa_nova.projeto = projeto
            alternativa_nova.save()

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

    if request.method == 'POST':
        criterio_form = CriterioForm(request.POST)
        if criterio_form.is_valid():
            criterio_novo = criterio_form.save()
            criterio_novo.projeto = projeto
            criterio_novo.save()
    
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
    - avaliar criterios (cada decisor) - OK
    - avaliar alternativas (cada decisor) ==> outra view
    - normalizar para gerar lista de pesos
    - calcular peso final
    - normalizar alternativas
    - somar alternativa por criterio
    - 
    
    ''' 
    template_name = 'avaliar_criterios.html'
    projeto_id = projeto_id
    projeto = Projeto.objects.get(id=projeto_id)
    decisores = list(Decisor.objects.filter(projeto=projeto_id, avaliou_criterios=False).values_list('id', 'nome'))
    criterios_id = Criterio.objects.filter(projeto=projeto_id).values_list('id', flat=True)

    if not decisores:
        return redirect('avaliaralternativas', projeto_id)

    combinacoes_criterios = _gerar_combinacoes_criterios(criterios_id)

    criterios_combinados = []
    for i in combinacoes_criterios:
        nome_criterio1 = Criterio.objects.get(id=i[0]).nome
        nome_criterio2 = Criterio.objects.get(id=i[1]).nome

        criterios_combinados.append(
            (nome_criterio1, nome_criterio2, i[0], i[1])
        )

    if request.method == 'POST':
        decisor_id = request.POST['decisor_id']
        campos = request.POST.keys()
        decisor = Decisor.objects.get(id=decisor_id)

        for campo in campos:
            if campo.startswith('c') and not campo.startswith('csrf'):
                print('{} => {}'.format(campo, request.POST[campo]))
                avaliacao = AvaliacaoCriterios(
                    projeto=projeto,
                    decisor=decisor,
                    criterios=campo,
                    valor=request.POST[campo]
                )
                avaliacao.save()

        decisor.avaliou_criterios = True
        decisor.save()

        return redirect('avaliarcriterios', projeto_id)

    return render(request, template_name, {
                'decisores': decisores,
                'criterios_combinados': criterios_combinados,
                'projeto_nome': projeto.nome,
                })

        # grava no banco 
        # tabela avaliação_criterios
        # projeto = projeto_id  ||  Carros   ||  Carros
        # decisor = decisor.id  ||  Diego    ||  Zenon
        # criterios = criterios ||  c1c2     ||  c1c2
        # valor = 3             ||  3        ||  2
        # print(f'd{decisor1.id}{criterios}')
        # avaliacao_criterios = AvaliacaoCriterios.objects.filter(projeto=projeto_id)
        # avaliacao_criterios = []
     

def avaliaralternativas(request, projeto_id):
    template_name = 'avaliar_alternativas.html'
    projeto_id = projeto_id
    projeto = Projeto.objects.get(id=projeto_id)
    decisores = list(Decisor.objects.filter(projeto=projeto_id, avaliou_alternativas=False).values_list('id', 'nome'))
    alternativas_id = Alternativa.objects.filter(projeto=projeto_id).values_list('id', flat=True)
    criterios = Criterio.objects.filter(projeto=projeto_id)

    if not decisores:
        return redirect('resultado', projeto_id)

    combinacoes_alternativas = _gerar_combinacoes_criterios(alternativas_id)

    alternativas_combinadas = []
    for i in combinacoes_alternativas:
        nome_alternativa1 = Alternativa.objects.get(id=i[0]).nome
        nome_alternativa2 = Alternativa.objects.get(id=i[1]).nome

        alternativas_combinadas.append(
            (nome_alternativa1, nome_alternativa2, i[0], i[1])
        )

    if request.method == 'POST':
        decisor_id = request.POST['decisor_id']
        campos = request.POST.keys()
        decisor = Decisor.objects.get(id=decisor_id)

        for campo in campos:
            if campo.startswith('c') and not campo.startswith('csrf'):
                print('{} => {}'.format(campo, request.POST[campo]))
                criterio_id = campo[1]
                criterio = Criterio.objects.get(id=criterio_id)

                avaliacao = AvaliacaoAlternativa(
                    projeto=projeto,
                    decisor=decisor,
                    criterio=criterio,
                    alternativas=campo,
                    valor=request.POST[campo],
                )
                avaliacao.save()

        decisor.avaliou_alternativas = True
        decisor.save()

        return redirect('avaliaralternativas', projeto_id)

    return render(request, template_name, {
                'decisores': decisores,
                'alternativas_combinadas': alternativas_combinadas,
                'criterios': criterios,
                'projeto_nome': projeto.nome,
                })

    '''
    para cada criterio cadastrado avalia 2 alternativas
    ex.: 3 criterios e 3 alternativas cadatrados
    c1a1a2  |  c1a1a3  |  c1a2a3
    c2a1a2  |  c2a1a3  |  c2a2a3
    c3a1a2  |  c3a1a3  |  c3a2a3
    '''

    # grava no banco 
        # tabela avaliação_alternativas
        # projeto = projeto_id        ||  Carros   ||  Carros
        # decisor = decisor_id        ||  Diego    ||  Zenon
        # criterio = criterio_id      ||  c1       ||  c1
        # alternativas = alternativas ||  a1a2     ||  a1a3
        # valor = 3                   ||  3        ||  2
        
        # avaliacao_alternativas = AvaliacaoAlternativas.objects.filter(projeto=projeto_id)
        # avaliacao_alternativas = []






def _normalizar(lista_elementos):
    return "teste"









def resultado(request, projeto_id):
    template_name = 'resultado.html'
    projeto_id = projeto_id
    projeto = Projeto.objects.get(id=projeto_id)

    '''
    projeto = models.ForeignKey('Projeto', on_delete=models.CASCADE)
    decisor = models.ForeignKey('Decisor', on_delete=models.CASCADE)
    criterios = models.CharField(max_length=20)
    valor = models.IntegerField()
    '''


    # calcula o peso para o decisor 1
    # TODO: deixar generico para pegar todos os decisores
    criterios_decisor_1 = AvaliacaoCriterios.objects.filter(decisor=1)
    # qtd_criterios = 4 # pegar todos os criterios cadastrados pelo projeto
    qtd_criterios = Criterio.objects.filter(projeto=projeto_id).count()



    ###################### TESTES ################################################################# 
    criterios = ['c1c2', 'c1c3', 'c1c4', 'c2c3', 'c2c4', 'c3c4']
    criterios_neg = ['c1c2 *-1', 'c1c3 *-1', 'c1c4 *-1', 'c2c3 *-1', 'c2c4 *-1', 'c3c4 *-1']
    matriz = [[0, 2, 3, 4], [1, 0, 3, 4], [1, 2, 0, 4], [1, 2, 3, 0]]
    matriz = [[0], [1, 0], [1, 2, 0], [1, 2, 3, 0]]

    # gerar matriz de acordo com numero de criterios
    matriz = []
    for i in range(qtd_criterios):
        matriz.append(list(range(1,qtd_criterios+1)))

    # posiciona o zero na matriz gerada
    pos_zero = 1
    for lista in matriz:
        lista[pos_zero-1] = 0
        pos_zero +=1

    # remove os elementos após o 0
    for lista in matriz:
        zero_p = lista.index(0)
        for i in lista[zero_p+1:]:
            lista.remove(i)

    # separa os criterios em um dicionario
    dic_ = {}
    for i in range(1,qtd_criterios+1):
        key = 'c{}'.format(i)
        dic_[key] = []
    
    for i in criterios:
        k=i[:2]
        dic_[k].append(i)

    # for k in dic_.keys():
    #     for i in criterios:
    #         if i.startswith(k):
    #             dic_[k].append(i)


    # for i in dic_.values():
    #     for j in matriz:
    #         lista_nova.append(j+i)

###################### TESTES #################################################################
 

    resultado = criterios_decisor_1
    criterios_nome = [ i.criterios for i in resultado ]
    criterios = [ i.valor for i in resultado ]
    
    print('criterios_nome')
    print(criterios_nome)
    print('criterios_nome')
    print(criterios)
    print('\n--------\n')

    ### aqui começa a rodar para cada DECISOR
    ### 1 - gerar matriz base
    matriz_base = []
    for i in range(qtd_criterios):
        matriz_base.append(list(range(1,qtd_criterios+1)))

    print('matriz_base')
    print(matriz_base)
    print('\n--------\n')


    ### 2 - posicionar zeros na matriz base
    pos_zero = 1
    for lista in matriz_base:
        lista[pos_zero-1] = 0
        pos_zero +=1

    print('matriz_base com zeros')
    print(matriz_base)
    print('\n--------\n')

    ### 3 - gerar nova matriz com valores positivos após o zero
    # remove os elementos após o 0
    for lista in matriz_base:
        zero_p = lista.index(0)
        for i in lista[zero_p+1:]:
            lista.remove(i)

    # separa os criterios em um dicionario
    dic_ = {}
    for i in range(1,qtd_criterios+1):
        key = 'c{}'.format(i)
        dic_[key] = []
    
    # for i in criterios_nome:
    #     k=i[:2]
    #     dic_[k].append(i)

    for i in criterios_decisor_1:
        k = i.criterios[:2]
        dic_[k].append(i.valor)

    
    print('dicionario de criterios dic_')
    print(dic_)
    print('\n--------\n')

    # complea a matriz com valores positivos
    matriz_com_positivos = _completa_matriz_com_positivos(matriz_base, dic_, qtd_criterios)

    print('matriz completa com positivos')
    print(matriz_com_positivos)
    print('\n--------\n')


    # 6 - gerar nova matriz com valores negativos antes do zero
    matriz_final = _completa_matriz_com_negativos(matriz_com_positivos, dic_, qtd_criterios, criterios_decisor_1)

    print('matriz final com negativos')
    print(matriz_final)
    print('-----------------')
    for i in matriz_final:
        print(i)
    print('\n--------\n')

    return render(request, template_name, {
        'projeto_nome': projeto.nome,
        'resultado': resultado,
        })


def _completa_matriz_com_positivos(matriz, dic, qtd_criterios):
    # funcao para completar matriz com numeros positivos

    matriz_nova = []
    for i in matriz:
        l = []
        for j in dic.values():
            if len(matriz_nova) < qtd_criterios:
                l = i+j
                matriz_nova.append(l)
    return matriz_nova

def _completa_matriz_com_negativos(matriz_n, dic, qtd_criterios, criterios_decisor_1):
    print('funcao linda de deus')
    
    criterios = {k:v for (v, k) in enumerate(dic.keys())}
    print(criterios)

    for i in criterios_decisor_1:
        print(i.criterios, i.valor)
        k=i.criterios[-2:]
        indice = criterios[k]
        el = '{}*-1'.format(i.valor)
        matriz_n[indice].insert(0, el)

        print('valor', el)

    return matriz_n



#### gerar combinacoes #####
from itertools import product

# mudar para _gerar_combinacoes(criterios/alternativas)
def _gerar_combinacoes_criterios(criterios):
    criterios_keys = criterios
    
    # criterios_keys = criterios.keys()
    # criterios_keys = ['c1', 'c2', 'c3', 'c4']

    # permsList = []
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
