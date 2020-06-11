import logging

logger = logging.getLogger(__name__)


class AlternativaService:

    @staticmethod
    def _gerar_matriz_base(qtd_alternativas):
        matriz_base = []
        for i in range(qtd_alternativas):
            matriz_base.append(list(range(1, qtd_alternativas + 1)))

        return matriz_base

    @staticmethod
    def _gerar_matriz(qtd_alternativas, matriz_base, lista_avaliacao):
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
            lista[pos_zero - 1] = 0
            pos_zero += 1

        logger.info('Zeros posicionados na matriz: {}'.format(matriz))

        ## remove valores apos zeros
        # [0]
        # [1, 0]
        # [1, 2, 0]
        # [1, 2, 3, 0]
        for lista in matriz:
            zero_p = lista.index(0)
            for i in lista[zero_p + 1:]:
                lista.remove(i)

        ## completar com positivos
        # [0, 1, 2, 3]
        # [1, 0, 1, 3]
        # [1, 2, 0, 1]
        # [1, 2, 3, 0]

        count = 0
        while count < qtd_alternativas:
            for i in list(lista_avaliacao):
                # if len(matriz[count]) < 4:
                if len(matriz[count]) < qtd_alternativas:
                    matriz[count].append(i)
                    lista_avaliacao.remove(i)
            count += 1

        logger.info('Matriz com valores positivos: {}'.format(matriz))

        ## completar com negativos
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
                if len(matriz[i + 1]) < qtd_alternativas:
                    matriz[i + 1].insert(0, v * -1)

        logger.info('Matriz final: {}'.format(matriz))

        return matriz

    def gerar_matrizes(self, d_matrizes, d_avaliacoes, qtd_alternativas):
        for k, v in d_avaliacoes.items():
            for idx, val in enumerate(v):
                matriz_base = self._gerar_matriz_base(qtd_alternativas)
                lista_avaliacao = val
                matriz = self._gerar_matriz(qtd_alternativas, matriz_base,
                                                           lista_avaliacao)
                d_matrizes[k].append(matriz)

        logger.info('Matrizes de Avaliações de alternativas: {}'.format(d_avaliacoes))

        return d_matrizes

    def _normalizar_alternativas(self, lista_elementos):
        lista_dos_somados = []
        lista_normalizada = []

        for elemento in lista_elementos:
            soma = sum(elemento)
            lista_dos_somados.append(soma)

        for elemento_da_soma in lista_dos_somados:
            maior, menor = max(lista_dos_somados), min(lista_dos_somados)
            if maior == menor:
                regular = 0
            else:
                regular = ((elemento_da_soma - menor) / (maior - menor))

            lista_normalizada.append(regular)

        return lista_normalizada

    def _soma_alternativa_por_criterio(self, lista_elementos):
        num_elementos = len(lista_elementos[0]) - 1
        lista_somada = []
        i = 0
        while i <= num_elementos:
            soma = sum([item[i] for item in lista_elementos])
            i = i + 1
            lista_somada.append(soma)
        return lista_somada


    def _multiplica_final(self, lista_elementos, lista_pesos):
        num_elementos = len(lista_elementos[0])

        lista_somada = []

        i = 0
        while i < num_elementos:
            lista_primeiros_elementos = []
            lista_primeiros_elementos = [item[i] for item in lista_elementos]
            lista_multi = []

            for numint, peso in enumerate(lista_pesos):
                multi = peso * lista_primeiros_elementos[numint]
                lista_multi.append(multi)

            i = i + 1
            lista_somada.append(sum(lista_multi))
        return lista_somada

    def calcular_resultado(self, matrizes, qtd_criterios, peso_final):
        # 1) Soma alternativas por criterio
        avaliacoes_alternativas = []
        for i in range(qtd_criterios):
            avaliacoes_alternativas.append(list())

        count = 1
        idx = 0

        # while count <= qtd_alternativas:
        while count <= qtd_criterios:
            for k, v in matrizes.items():
                s = self._normalizar_alternativas(v[idx])
                avaliacoes_alternativas[idx].append(s)
            idx += 1
            count += 1

        lista_somas = []
        for lista_elementos in avaliacoes_alternativas:
            soma = self._soma_alternativa_por_criterio(lista_elementos)
            lista_somas.append(soma)

        logger.info('Alternativas por critério: {}'.format(avaliacoes_alternativas))

        # 2) Multiplica pelo peso
        resultado_um = self._multiplica_final(lista_somas, peso_final)

        logger.info('Alternativas multiplicadas pelo peso: {}'.format(resultado_um))

        return resultado_um
