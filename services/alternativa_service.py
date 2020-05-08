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
