from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from core.forms import DecisorForm, NomeProjetoForm, AlternativaForm, CriterioForm
from core.models import Projeto, Decisor, Alternativa, Criterio, AvaliacaoCriterios, AvaliacaoAlternativas


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

        for campo in campos:
            if campo.startswith('c') and not campo.startswith('csrf'):
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

        for campo in campos:
            if campo.startswith('c') and not campo.startswith('csrf'):
                criterio_id = campo[1]
                criterio = Criterio.objects.get(id=criterio_id)

                avaliacao = AvaliacaoAlternativas(
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


def resultado(request, projeto_id):
    '''
    projeto = models.ForeignKey('Projeto', on_delete=models.CASCADE)
    decisor = models.ForeignKey('Decisor', on_delete=models.CASCADE)
    criterios = models.CharField(max_length=20)
    valor = models.IntegerField()
    '''

    template_name = 'resultado.html'
    projeto_id = projeto_id
    projeto = Projeto.objects.get(id=projeto_id)
    qtd_criterios = Criterio.objects.filter(projeto=projeto_id).count()
    qtd_alternativas = Alternativa.objects.filter(projeto=projeto_id).count()
    decisores = projeto.decisores.all()
    criterios = Criterio.objects.filter(projeto=projeto_id)

    matrizes = []
    for decisor in decisores:
        criterios_decisor = AvaliacaoCriterios.objects.filter(projeto=projeto_id, decisor=decisor.id)
        matriz = _gerar_matriz(qtd_criterios, criterios_decisor)
        matrizes.append(matriz)

    # calcular pesos dos decisores
    pesos_decisores = []
    for matriz in matrizes:
        peso_matriz = _normalizar(matriz)
        pesos_decisores.append(peso_matriz)

    print('PESO DECISORE ==>>', pesos_decisores) 

    # calcular o peso final 
    peso_final = _peso_criterios(pesos_decisores)
    print('CALCULA PESO FINAL ==>>', peso_final) 

    # gera matriz de alternativa para cada decisor
    '''
    projeto = models.ForeignKey('Projeto', on_delete=models.CASCADE)
    decisor = models.ForeignKey('Decisor', on_delete=models.CASCADE)
    criterio = models.ForeignKey('Criterio', on_delete=models.CASCADE)
    alternativas = models.CharField(max_length=20)
    valor = models.IntegerField()
    '''
    
    # matriz_alternativa = AvaliacaoCriterios.objects.filter(projeto=projeto_id, decisor=decisor.id)
    # matriz_alternativa_1 = AvaliacaoAlternativas.objects.filter(projeto=projeto_id, decisor=1)
    

    matrizes_alt = {}
    for decisor in decisores:
        for criterio in criterios:
            # criterios_decisor = AvaliacaoAlternativas.objects.filter(projeto=projeto_id, decisor=decisor.id, criterio=criterio.id)
            k1 = 'd{}'.format(decisor.id)
            # k2 = 'c{}'.format(criterios_decisor.values('criterio')[0]['criterio'])
            k2 = '{}'.format(criterio.codigo)
            # print(k2)
            matrizes_alt[k1] = {k2:[]}
    # for decisor in decisores:
    #     for criterio in criterios:
    #         criterios_decisor = AvaliacaoAlternativas.objects.filter(projeto=projeto_id, decisor=decisor.id, criterio=criterio.id)
    #         k1 = 'd{}'.format(decisor.id)
    #         k2 = 'c{}'.format(criterios_decisor.values('criterio')[0]['criterio'])
    #         matrizes_alt[k1] = {k2:[]}
    for decisor in decisores:
        for criterio in criterios:
            criterios_decisor = AvaliacaoAlternativas.objects.filter(projeto=projeto_id, decisor=decisor.id, criterio=criterio.id)
            # print('CARAKAAAAAAAAA')
            # print(criterio)
            print(criterios_decisor)
            matriz = _gerar_matriz_alt(qtd_alternativas, criterios_decisor)
            k1 = 'd{}'.format(decisor.id)
            # k2 = 'c{}'.format(criterios_decisor.values('criterio')[0]['criterio'])
            k2 = '{}'.format(criterio.codigo)
            # print(k2)
            matrizes_alt[k1][k2] = matriz
    # for decisor in decisores:
    #     for criterio in criterios:
    #         criterios_decisor = AvaliacaoAlternativas.objects.filter(projeto=projeto_id, decisor=decisor.id, criterio=criterio.id)
    #         matriz = _gerar_matriz_alt(qtd_alternativas, criterios_decisor)
    #         k1 = 'd{}'.format(decisor.id)
    #         k2 = 'c{}'.format(criterios_decisor.values('criterio')[0]['criterio'])
    #         matrizes_alt[k1][k2] = matriz

    print('\nMATRIZZZZZZ ALT\n')
    print('matrizes alt ', matrizes_alt)

    # normalizar listas
    matrizes_alt_normalizadas = {}
    for decisor in decisores:
        for criterio in criterios:
            criterios_decisor = AvaliacaoAlternativas.objects.filter(projeto=projeto_id, decisor=decisor.id, criterio=criterio.id)
            k1 = 'd{}'.format(decisor.id)
            # k2 = 'c{}'.format(criterios_decisor.values('criterio')[0]['criterio'])
            k2 = '{}'.format(criterio.codigo)
            matrizes_alt_normalizadas[k1] = {k2:[]}
    # for decisor in decisores:
    #     for criterio in criterios:
    #         criterios_decisor = AvaliacaoAlternativas.objects.filter(projeto=projeto_id, decisor=decisor.id, criterio=criterio.id)
    #         k1 = 'd{}'.format(decisor.id)
    #         k2 = 'c{}'.format(criterios_decisor.values('criterio')[0]['criterio'])
    #         matrizes_alt_normalizadas[k1] = {k2:[]}


    for decisor in decisores:
        for criterio in criterios:
            criterios_decisor = AvaliacaoAlternativas.objects.filter(projeto=projeto_id, decisor=decisor.id, criterio=criterio.id)
            k1 = 'd{}'.format(decisor.id)
            # k2 = 'c{}'.format(criterios_decisor.values('criterio')[0]['criterio'])
            k2 = '{}'.format(criterio.codigo)
            for k,v in matrizes_alt.items():
                for l,u in v.items():
                    matrizes_alt_normalizadas[k1][k2] = _normalizar_alternativas(u)
    # for decisor in decisores:
    #     for criterio in criterios:
    #         criterios_decisor = AvaliacaoAlternativas.objects.filter(projeto=projeto_id, decisor=decisor.id, criterio=criterio.id)
    #         k1 = 'd{}'.format(decisor.id)
    #         k2 = 'c{}'.format(criterios_decisor.values('criterio')[0]['criterio'])
    #         for k,v in matrizes_alt.items():
    #             for l,u in v.items():
    #                 matrizes_alt_normalizadas[k1][k2] = _normalizar_alternativas(u)

    print('\nMATRIZZZZZZ ALT NORMALIZADAS\n')
    print('matrizes alt norm. ', matrizes_alt_normalizadas)


    # soma as alternativas
    soma_alternativas = {}
    for decisor in decisores:
        for criterio in criterios:
            criterios_decisor = AvaliacaoAlternativas.objects.filter(projeto=projeto_id, decisor=decisor.id, criterio=criterio.id)
            k1 = 'd{}'.format(decisor.id)
            # k2 = 'c{}'.format(criterios_decisor.values('criterio')[0]['criterio'])
            k2 = '{}'.format(criterio.codigo)
            soma_alternativas[k2] = []
    # for decisor in decisores:
    #     for criterio in criterios:
    #         criterios_decisor = AvaliacaoAlternativas.objects.filter(projeto=projeto_id, decisor=decisor.id, criterio=criterio.id)
    #         k1 = 'd{}'.format(decisor.id)
    #         k2 = 'c{}'.format(criterios_decisor.values('criterio')[0]['criterio'])
    #         soma_alternativas[k2] = []

    

    for k,v in matrizes_alt_normalizadas.items():
        # print(k,v)

        for l,u in v.items():
            soma_alternativas[l].append(u)

    for k,v in soma_alternativas.items():

        print(k,v)
        print('========')
        soma = _soma_alternativa_por_criterio(v)
        soma_alternativas[k] = soma

    print('SOMA DAS ALTERNATIVAS', soma_alternativas)

    # multiplica para achar o resultado
    lista_somas = list(soma_alternativas.values())
    print('lista_somas', lista_somas)

    print('peso_final', peso_final)
    resultado_um = _multiplica_final(lista_somas, peso_final)
    alternativas = Alternativa.objects.filter(projeto=projeto_id)
    
    print('\n###########\n')
    
    print('resposta do _multiplica_final', resultado_um)
    print('\n###########\n')


    resultado = []
    count = 0

    # print('LLLEEENNNN ALTERNAS', len(alternativas))
    # print('ALTERNATIVAS ==>', alternativas)
    # print('resultados_um ==', resultado_um)
    while count < len(alternativas):
        # print('count', count)
        # print('res', resultado)
        # print('alterna', alternativas)
        resultado.append( 
            (alternativas[count], resultado_um[count]) 
        )
        count += 1

    # print('LLLEEENNNN ALTERNAS', len(alternativas))
    # print(alternativas)
    # while count < len(alternativas):
    #     print('count', count)
    #     print('res', resultado)
    #     print('alterna', alternativas)
    #     resultado.append( 
    #         (alternativas[count], resultado_um[count]) 
    #     )
    #     count += 1

    resultado.sort(key=lambda x: x[1] ,reverse=True)


    return render(request, template_name, {
        'projeto_nome': projeto.nome,
        'resultado': resultado,
        'peso_final': peso_final,
        'criterios': criterios,
        })

######## aux functions   ########

def _inclui_decisor_no_projeto(projeto, decisor):
    projeto.decisores.add(decisor)
    return


def _gerar_matriz(qtd_criterios, criterios_decisor):
    ### 1 - gerar matriz base
    matriz_base = []
    for i in range(qtd_criterios):
        matriz_base.append(list(range(1,qtd_criterios+1)))

    ### 2 - posicionar zeros na matriz base
    pos_zero = 1
    for lista in matriz_base:
        lista[pos_zero-1] = 0
        pos_zero +=1

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

    for i in criterios_decisor:
        k = i.criterios[:2]
        dic_[k].append(i.valor)

    # completa a matriz com valores positivos
    matriz_com_positivos = _completa_matriz_com_positivos(matriz_base, dic_, qtd_criterios)

    ### 4 - gerar nova matriz com valores negativos antes do zero
    matriz_final = _completa_matriz_com_negativos(matriz_com_positivos, dic_, qtd_criterios, criterios_decisor)

    return matriz_final


def _gerar_matriz_alt(qtd_criterios, criterios_decisor):
    ### 1 - gerar matriz base
    matriz_base = []
    for i in range(qtd_criterios):
        matriz_base.append(list(range(1,qtd_criterios+1)))

    print('\n>>>>> GERAR_MATRIZ_ALT')
    print('matriz_base', matriz_base)

    ### 2 - posicionar zeros na matriz base
    pos_zero = 1
    for lista in matriz_base:
        lista[pos_zero-1] = 0
        pos_zero +=1

    # print('>>>>> GERAR_MATRIZ_ALT')
    print('matriz_base com zeros', matriz_base)

    ### 3 - gerar nova matriz com valores positivos após o zero
    # remove os elementos após o 0
    for lista in matriz_base:
        zero_p = lista.index(0)
        for i in lista[zero_p+1:]:
            lista.remove(i)

    # separa os criterios em um dicionario
    import collections
    dic_ = collections.OrderedDict()
    # dic_ = {}
    for i in range(1,qtd_criterios+1):
        key = 'a{}'.format(i)
        dic_[key] = []

    for i in criterios_decisor:
        print('i', i.alternativas)
        print('i', i.valor)
        k = i.alternativas[2:4]
        dic_[k].append(i.valor)

    print('\n>>>>>>>>>>>>>>>>>>>>>>>')
    print('dicionario malucao', dic_)
    print('>>>>>>>>>>>>>>>>>>>>>>>>>')

    # completa a matriz com valores positivos
    matriz_com_positivos = _completa_matriz_com_positivos(matriz_base, dic_, qtd_criterios)
    print('matriz com positivos', matriz_com_positivos)

    ### 4 - gerar nova matriz com valores negativos antes do zero
    matriz_final = _completa_matriz_com_negativos_alt(matriz_com_positivos, dic_, qtd_criterios, criterios_decisor)
    print('matriz final', matriz_final)

    return matriz_final


def _completa_matriz_com_positivos(matriz, dic, qtd_criterios):
    matriz_nova = []
    for i in matriz:
        l = []
        for j in dic.values():
            if len(matriz_nova) < qtd_criterios:
                l = i+j
                matriz_nova.append(l)
    return matriz_nova

def _completa_matriz_com_negativos(matriz_n, dic, qtd_criterios, criterios_decisor):
    criterios = {k:v for (v, k) in enumerate(dic.keys())}

    for i in criterios_decisor:
        k=i.criterios[-2:]
        indice = criterios[k]
        el = i.valor * -1
        matriz_n[indice].insert(0, el)

    return matriz_n


def _completa_matriz_com_negativos_alt(matriz_n, dic, qtd_criterios, criterios_decisor):
    criterios = {k:v for (v, k) in enumerate(dic.keys())}

    for i in criterios_decisor:
        k=i.alternativas[-2:]
        indice = criterios[k]
        el = i.valor * -1
        matriz_n[indice].insert(0, el)

    return matriz_n


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


def _separa_elementos(lista_elementos, idx):
    '''
    Funcao que separa lista de listas pelo indice.

    Ex.:
    INPUT:
    lista_de_listas = [
        [0.3333, 1, 2, 3], 
        [0.3333, 1, 2, 3], 
        [0.3333, 1, 2, 3]
    ]

    _separa_elementos(lista_de_listas, 0)

    OUTPUT:
    [0.33333, 0.33333, 0.33333]
    '''
    lista_separada = []
    for l in lista_elementos:
        lista_separada.append(l[idx])
    return lista_separada


def _peso_criterios(lista_elementos):
    num_elementos = len(lista_elementos[0])

    soma_pesos = []
    for idx in range(num_elementos):
        lista_temp = []
        lista_temp = _separa_elementos(lista_elementos, idx)
        soma_pesos.append(sum(lista_temp))

    return soma_pesos


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


def _normalizar_alternativas(lista_elementos):
    lista_dos_somados = []
    lista_normalizada = []
    
    for elemento in lista_elementos:
        soma = sum(elemento)
        lista_dos_somados.append(soma)
    
    for elemento_da_soma in lista_dos_somados:
        maior , menor = max(lista_dos_somados), min(lista_dos_somados)
        if maior == menor :
            regular = 0
        else:
            regular = ((elemento_da_soma - menor)/(maior - menor))
        lista_normalizada.append(regular)
    
    return lista_normalizada

def _soma_alternativa_por_criterio(lista_elementos):
    print('\n====== _SOMA_ALTERNATIVA_POR_CRITERIO ======')
    print('lista_elementos ', lista_elementos)

    num_elementos = len(lista_elementos) -1
    lista_somada = []
    i = 0
    while i <= num_elementos:
        soma = sum([item[i] for item in lista_elementos])
        i =  i+ 1
        lista_somada.append(soma)
    
    print('lista_somada', lista_somada)

    return lista_somada


def _separa_primeiros_elementos(lista_elementos, idx):
    print('\n====== _SEPARA_PRIMEIROS_ELEMENTOS ======')

    lista_separada = []
    print('tamanho lista_elementos',len(lista_elementos))
    print('lista_elementos', lista_elementos)
    for item in lista_elementos:
        # print('item', item[idx])
        # if idx < len(lista_elementos)-1:
        lista_separada.append(item[idx])
        
    print('lista_separada' ,lista_separada)
    return lista_separada


def _multiplicar_pelo_peso(lista_primeiros_elementos ,lista_pesos):
    lista_multi = []
    # print('aqui ó',lista_primeiros_elementos)
    for numint, peso in enumerate(lista_pesos):
        # print('>>>>>>>>>>>>>>>>>> CAPETA')
        # print('numint', lista_primeiros_elementos[numint])
        # print('peso', peso)
        multi = peso * lista_primeiros_elementos[numint]
        lista_multi.append(multi)

    # print('lista_multi', lista_multi)
    return lista_multi


def _multiplica_final(lista_elementos, lista_pesos):
    print('\n====== MULTIPLICA_FINAL ======')
    print('lista_elementos', lista_elementos)

    num_elementos = len(lista_elementos)
    lista_somada = []

    for idx in range(num_elementos):
        lista_primeiros_el = _separa_primeiros_elementos(
                                lista_elementos, 
                                idx)

        lista_multiplicada = _multiplicar_pelo_peso(
            lista_primeiros_el, lista_pesos
        )
        # print('caceta', lista_multiplicada)

        lista_somada.append(sum(lista_multiplicada))
        print('lista_somadaaaaaa', lista_somada)
        print('idx', idx)
    return lista_somada