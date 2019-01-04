from django.shortcuts import render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from core.forms import DecisorForm, NomeProjetoForm, AlternativaForm, CriterioForm
from core.models import Projeto, Decisor, Alternativa, Criterio, AvaliacaoCriterios, AvaliacaoAlternativas
import collections

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

    return render(request, template_name, {
                'nome_projeto_form': nome_projeto_form,
                'projetos': projetos})


def metodo(request):
    template_name = 'metodo.html'
    return render(request, template_name)


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


def editardados(request):
    nome = request.POST['nome']
    tipo_id = request.POST['tipoId'].split(':') 
    tipo = tipo_id[0]
    _id,  = tipo_id[1]
    
    if tipo == 'projeto':
        projeto = Projeto.objects.get(id=_id)
        projeto.nome = _nome
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

    if request.method == 'POST':
        decisor_form = DecisorForm(request.POST)
        if decisor_form.is_valid():
            decisor_novo = decisor_form.save()
            _inclui_decisor_no_projeto(projeto, decisor_novo)
            decisor_novo.projeto = projeto
            decisor_novo.save()
        return redirect('cadastradecisores', projeto_id=projeto.id)

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

    #### Criterios ####

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

    # calcular o peso final 
    peso_final = _peso_criterios(pesos_decisores)
    print('PESO FINALLLLLLL', peso_final)

    # cria tupla de criterio e peso para renderizar
    pesos_criterios = []
    pos_peso = 0
    peso_final_qt = len(peso_final)
    
    while pos_peso < peso_final_qt:
        for criterio in criterios:
            pesos_criterios.append((criterio.nome, peso_final[pos_peso]))
            pos_peso += 1

    #gera dicionario de matrizes
    d_matrizes = {}
    for decisor in decisores:
        k = 'D{}'.format(decisor.id)
        d_matrizes[k] = []

    # gera dicionario de avaliacoes
    d_avaliacoes = {}
    for decisor in decisores:
        k = 'D{}'.format(decisor.id)
        d_avaliacoes[k] = []
        for i in range(qtd_alternativas):
            d_avaliacoes[k].append(list())

    # print('ZZZZZZZZ')
    # print(d_avaliacoes)
    # print('ZZZZZZZZ')

    lista_criterios = []
    for c in criterios:
        lista_criterios.append(c.codigo)      

    # avaliacoes_alt = AvaliacaoAlternativas.objects.filter(projeto=projeto_id, decisor=14, criterio__codigo='c4').order_by('alternativas')
    avaliacoes_alt = AvaliacaoAlternativas.objects.filter(projeto=projeto_id).order_by('alternativas')

    for i in avaliacoes_alt:
        k = 'D{}'.format(i.decisor.id)
        indice = lista_criterios.index(i.criterio.codigo)
        # print('indice', indice)
        d_avaliacoes[k][indice].append(i.valor)
    

    # gera matrizes
    matriz_base_alt = []
    for i in range(qtd_criterios):
        matriz_base_alt.append(list(range(1,qtd_criterios+1)))

    for k,v in d_avaliacoes.items():
        print(k,v)
        # chama a funcao que recebe uma lista de avaliacoes e retorna uma matriz
        # coloca a matriz gerada dentro do dicionario de matrizes (d_matrizes)
        for idx, val in enumerate(v):
            matriz_base_alt = []
            for i in range(qtd_criterios):
                matriz_base_alt.append(list(range(1,qtd_criterios+1)))

            lista_avaliacao = val
            matriz = _gerar_matriz_alt(qtd_alternativas, matriz_base_alt, lista_avaliacao)
            d_matrizes[k].append(matriz)


    # soma alternativas por criterio
    avaliacoes_alternativas = []
    for i in range(qtd_alternativas):
        avaliacoes_alternativas.append(list())

    count = 1
    idx = 0

    while count <= qtd_alternativas:
        print('CRITERIO {}'.format(count))
        for k, v in d_matrizes.items():
            s = _normalizar_alternativas(v[idx])
            print(s)
            avaliacoes_alternativas[idx].append(s)
        idx += 1
        count += 1

    lista_somas = []
    for lista_elementos in avaliacoes_alternativas:
        soma = _soma_alternativa_por_criterio(lista_elementos)
        lista_somas.append(soma)

    resultado_um = _multiplica_final(lista_somas, peso_final)
    print(resultado_um)


    ####### Codigo antigo de alternativas #######
    #### Alternativas ####

    #gera matriz de alternativa para cada decisor
    # matrizes_alt = collections.OrderedDict()
    # for decisor in decisores:
    #     k1 = 'd{}'.format(decisor.id)
    #     for criterio in criterios:
    #         k2 = '{}'.format(criterio.codigo)
    #         matrizes_alt[k1] = {k2:[]}

    # count=1
    # for decisor in decisores:
    #     for criterio in criterios:
    #         criterios_decisor = AvaliacaoAlternativas.objects.filter(projeto=projeto_id, decisor=decisor.id, criterio=criterio.id)
    #         if criterios_decisor:
    #             # print('AGORA TEM ESSA BOSTA!')
    #             # print(count)
    #             count+=1
    #             matriz = _gerar_matriz_alt(qtd_alternativas, criterios_decisor)
    #             k1 = 'd{}'.format(decisor.id)
    #             k2 = '{}'.format(criterio.codigo)
    #             print('=== k2 ===> ', k2)
    #             matrizes_alt[k1][k2] = matriz

    ############
    ### Ideia ##
    ############
    # {d1: c1 [
    #     a1[1,2,3,4],
    #     a2[5,4,3,2],
    #     a3[8,7,6,5],
    #     a4[5,6,7,8]
    # ]

    # 1 - organizar avaliacoes poe decisor e criterio
    # 2 - gerar matrizes
    # - - - - prestar atenção na geração de matrizes (dicionario)


    #organiza as avaliacoes da seguinte forma
    #{d1: {c1} [
    #     {a1}[1,2,3,4],
    #     {a2}[5,4,3,2],
    #     {a3}[8,7,6,5],
    #     {a4}[5,6,7,8]
    # ]
    avaliacoes_alt_organizadas = collections.OrderedDict()
    for decisor in decisores:
        k1 = 'd{}'.format(decisor.id)
        avaliacoes_alt_organizadas[k1] = []
        for i in range(qtd_alternativas):
            avaliacoes_alt_organizadas[k1].append(list())

    # print('\nAAAAAAAAAAA>>>>>>>>>>>>>>>>>')
    # print(avaliacoes_alt_organizadas)
    # print('AAAAAAAAAAA>>>>>>>>>>>>>>>>>\n')

    # prepara lista dentro das avaliacoes
    for k,i in avaliacoes_alt_organizadas.items():
        for i in range(qtd_alternativas):
            c = 0
            while c < qtd_alternativas:
                avaliacoes_alt_organizadas[k][i].append(list())
                c += 1
        
    
    # print('\navaliacoes_alt_organizadas')
    # for k, v in avaliacoes_alt_organizadas.items():
    #     print(k, v)
    # print(' avaliacoes_alt_organizadas\n')


    avaliacoes_alt = AvaliacaoAlternativas.objects.filter(projeto=projeto_id)

    for avaliacao in avaliacoes_alt:
        
    #     texto = 'D{} - {}'.format(
    #                                 avaliacao.decisor.id,
    #                                 # avaliacao.criterio,
    #                                 # avaliacao.criterio.codigo,
    #                                 # avaliacao.alternativas,
    #                                 avaliacao.valor,
                                # )
        # print('=======>>>>>>')
        # print(texto)
        # print('=======>>>>>>\n')
        
        # matriz = _gerar_matriz_alt(qtd_alternativas, avaliacao)
        k1 = 'd{}'.format(avaliacao.decisor.id)
        criterio_num = avaliacao.alternativas[-3]
        indice = int(criterio_num)-1
        for l in avaliacoes_alt_organizadas[k1]:
            # print(k1, 'xuxu beleza', l)
            l[indice].append(avaliacao.valor)
            
        # print('indice - alternativa', indice)
        # print('hr =========\n')
        # avaliacoes_alt_organizadas[k1][indice].append(avaliacao.valor)

        # matrizes_alt[k1].append(avaliacao.valor)

    # print('aaahhh lelek lek - avaliacoes_alt_organizadas')
    # for k,v in avaliacoes_alt_organizadas.items():
    #     print(k)
    #     for i in v:
    #         print(i)
    
    # matrizes_alt = collections.OrderedDict()
    # for decisor in decisores:
    #     k1 = 'd{}'.format(decisor.id)
    #     matrizes_alt[k1] = []
    
    # for decisor in decisores:
    #     for criterio in criterios:
    #         criterios_decisor = AvaliacaoAlternativas.objects.filter(projeto=projeto_id, decisor=decisor.id, criterio=criterio.id)
    #         if criterios_decisor:
    #             matriz = _gerar_matriz_alt(qtd_alternativas, criterios_decisor)
    #             k1 = 'd{}'.format(decisor.id)
    #             k2 = '{}'.format(criterio.codigo)
    #             matrizes_alt[k1][k2] = matriz

    #### ERRO:
    #### matrizes_alt com valores zerados
    #### 'c4': [[0], [0], [0], [0]], 'c3': [[0], [0], [0], [0]]
    #### 'c3' ta vindo com queryset vazio
    #### 'c4' vem vazio tb
    # print('\n MATRIZES_ALT')
    # print(matrizes_alt)
    # print('\n fim MATRIZES_ALT\n')

    #gera matriz de alternativa normalizadas
    matrizes_alt_normalizadas = {}
    for decisor in decisores:
        for criterio in criterios:
            criterios_decisor = AvaliacaoAlternativas.objects.filter(projeto=projeto_id, decisor=decisor.id, criterio=criterio.id)
            k1 = 'd{}'.format(decisor.id)
            k2 = '{}'.format(criterio.codigo)
            matrizes_alt_normalizadas[k1] = {}

    for decisor in decisores:
        for criterio in criterios:
            criterios_decisor = AvaliacaoAlternativas.objects.filter(projeto=projeto_id, decisor=decisor.id, criterio=criterio.id)
            k1 = 'd{}'.format(decisor.id)
            k2 = '{}'.format(criterio.codigo)

            for k,v in matrizes_alt.items():
                for l,u in v.items():
                    matrizes_alt_normalizadas[k1][k2] = _normalizar_alternativas(u)

    # soma as alternativas
    alternativas_para_somar = collections.OrderedDict()
    for decisor in decisores:
        for criterio in criterios:
            criterios_decisor = AvaliacaoAlternativas.objects.filter(projeto=projeto_id, decisor=decisor.id, criterio=criterio.id)
            k2 = '{}'.format(criterio.codigo)
            alternativas_para_somar[k2] = []
    

    for k,v in matrizes_alt_normalizadas.items():
        for l,u in v.items():
            alternativas_para_somar[l].append(u)


    alternativas_ordenadas = collections.OrderedDict()
    for k,v in alternativas_para_somar.items():
        alternativas_ordenadas[k] = []

    # for i in alternativas_para_somar.values():
    #     print('i alternativas para somar',i)
    # print(alternativas_para_somar)

    for k,v in alternativas_para_somar.items():
        for i in range(len(alternativas_para_somar)):
            alternativas_ordenadas[k].append(
                _separa_alternativas(k, v, i)
            )

    # print('{{{{{{{{{{{{{{{{')
    # for i in alternativas_ordenadas.values():
    #     print('alternativas_ordenadas', i)

    lista_somas = _soma_alternativa_por_criterio(alternativas_ordenadas)

    resultado_um = _multiplica_final(lista_somas, peso_final)
    alternativas = Alternativa.objects.filter(projeto=projeto_id)

    resultado = []
    count = 0

    while count < len(alternativas):
        resultado.append( 
            (alternativas[count], resultado_um[count-1]) 
        )
        count += 1

    resultado.sort(key=lambda x: x[1] ,reverse=True)


    return render(request, template_name, {
        'projeto_nome': projeto.nome,
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
    dic_ = collections.OrderedDict()
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


## GERAR MATRIZES
def _gerar_matriz_alt(qtd_alternativas, matriz_base, lista_avaliacao):
    '''
    Funcao que gera as matrizes das alternativas
    Recebe <tal> e retorna <tal>

    Ex.:
    INPUT
    OUTPUT

    '''
    matriz = matriz_base

    ## posiciona zeros
    # [0, 1, 2, 3]
    # [1, 0, 1, 2]
    # [1, 2, 0, 1]
    # [1, 2, 3, 0]
    pos_zero = 1
    for lista in matriz:
        lista[pos_zero-1] = 0
        pos_zero += 1
        # print('pos_zero', pos_zero)
        


    ## remove valores apos zeros
    # [0]
    # [1, 0]
    # [1, 2, 0]
    # [1, 2, 3, 0]
    for lista in matriz:
        zero_p = lista.index(0)
        for i in lista[zero_p+1:]:
            lista.remove(i)


    ## completar com positivos
    # [0, 1, 2, 3]
    # [1, 0, 1, 3]
    # [1, 2, 0, 1]
    # [1, 2, 3, 0]
    
    count = 0
    while count < qtd_alternativas:
        for i in list(lista_avaliacao):
            if len(matriz[count]) < 4:
                matriz[count].append(i)
                lista_avaliacao.remove(i)
        count += 1


    ## completar com negativos
    qtd_alternativas = 4

    # 1) Remover os elementos antes do 0 (zero)
    # [0, 1, 2, 3]
    # [0, 1, 3]
    # [0, 1]
    # [0]
    pos_zero = 0
    c = 0
    for l in matriz:
        for i in l[:c]:
            l.remove(i)
        c += 1


    # 2) Multiplica -1 e completa as matrizes
    # [0, 1, 2, 3]
    # [-1, 0, 1, 3]
    # [-1, -2, 0, 1]
    # [-1, -3, -3, 0]
    for l in matriz:
        for i, v in enumerate(l[1:]):
            if len(matriz[i+1]) < qtd_alternativas:
                matriz[i+1].insert(0,v*-1)

    return matriz


def _gerar_matriz_alt_OLD(qtd_criterios, criterios_decisor):
    # print('\n FUNCAO _GERAR_MATRIZ_ALT - inicio')
    # print('qtd_criterios', qtd_criterios)
    # print('criterios_decisor', criterios_decisor)
    # print('criterios_decisor', criterios_decisor)


    ### 1 - gerar matriz base
    matriz_base = []
    for i in range(qtd_criterios):
        # matriz_base.append(list(range(1,qtd_criterios+1)))
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

    # print('\n MATRIZ BASE sem zeros')
    # print(matriz_base)
    # print('\n fim MATRIZES BASE\n')


    # separa os criterios em um dicionario
    dic_ = collections.OrderedDict()
    # dic_ = {}
    for i in range(1,qtd_criterios+1):
        key = 'a{}'.format(i)
        dic_[key] = []

    for i in criterios_decisor:
        # print(i.alternativas[2:4])
        # print(i.valor)
        k = i.alternativas[2:4] # a1
        dic_[k].append(i.valor) # 5

    # completa a matriz com valores positivos
    matriz_com_positivos = _completa_matriz_com_positivos(matriz_base, dic_, qtd_criterios)
    
    ### 4 - gerar nova matriz com valores negativos antes do zero
    matriz_final = _completa_matriz_com_negativos_alt(matriz_com_positivos, dic_, qtd_criterios, criterios_decisor)

    # print('matriz_final', matriz_final)

    # print('\n FUNCAO _GERAR_MATRIZ_ALT - fim')

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
    # print('\n NORMALIZAR ALTERNATIVAS\n')
    # print('lista elementos', lista_elementos)


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

    # print('lista_normalizada', lista_normalizada)
    # print('final: NORMALIZAR ALTERNATIVAS')


    return lista_normalizada


def _separa_alternativas(criterio, lista_elementos, idx):
    num_el = len(lista_elementos[0])
    lista_separada = []
    
    if idx < num_el:
        for item in lista_elementos:
            lista_separada.append(item[idx])
    return lista_separada


def _soma_alternativa_OLD(alternativas_ordenadas, idx):
    alternativas_somadas = []
    for i in alternativas_ordenadas:
        alternativas_somadas.append(sum(i[idx]))

    return alternativas_somadas


def _soma_alternativa_por_criterio(lista_elementos):
    num_elementos = len(lista_elementos[0]) -1
    lista_somada = []
    i = 0
    while i <= num_elementos:
        soma = sum([item[i] for item in lista_elementos])
        i =  i+ 1
        lista_somada.append(soma)
    return lista_somada


def _soma_alternativa_por_criterio_OLD(alternativas_ordenadas):
    alternativas_somadas = []

    for i in range(len(alternativas_ordenadas.values())):
        alternativas_somadas.insert(
            i,
            _soma_alternativa(alternativas_ordenadas.values(), i)
        )
    
    return  alternativas_somadas


def _separa_primeiros_elementos(lista_elementos, idx):
    
    lista_separada = []
    lista_separada = lista_elementos[idx]
        
    return lista_separada


def _multiplicar_pelo_peso(lista_primeiros_elementos ,lista_pesos):
    lista_multi = []
    for numint, peso in enumerate(lista_pesos):
  
        multi = peso * lista_primeiros_elementos[numint]
        lista_multi.append(multi)

    return lista_multi


def _multiplica_final(lista_elementos, lista_pesos):
    num_elementos = len(lista_pesos) 

    lista_somada = []
 
    i = 0
    while i < num_elementos:
        lista_primeiros_elementos = []
        lista_primeiros_elementos = [item[i] for item in lista_elementos]
        lista_multi = []

        for numint, peso in enumerate(lista_pesos):
            multi = peso * lista_primeiros_elementos[numint]
            lista_multi.append(multi)


        i =  i + 1
        lista_somada.append(sum(lista_multi))
    return lista_somada 


def _multiplica_final_OLD(lista_elementos, lista_pesos):
    num_elementos = len(lista_elementos)
    lista_somada = []

    for idx in range(num_elementos):
        lista_primeiros_el = _separa_primeiros_elementos(
                                lista_elementos, 
                                idx)

        lista_multiplicada = _multiplicar_pelo_peso(
            lista_primeiros_el, lista_pesos
        )

        lista_somada.append(sum(lista_multiplicada))

    return lista_somada