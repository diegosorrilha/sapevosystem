import collections
import logging

logger = logging.getLogger(__name__)


class Matriz:
    def _completa_matriz_com_positivos(self, matriz, dic, qtd_criterios):
        matriz_nova = []
        for i in matriz:
            l = []
            for j in dic.values():
                if len(matriz_nova) < qtd_criterios:
                    l = i + j
                    matriz_nova.append(l)
        return matriz_nova

    def _completa_matriz_com_negativos(self, matriz_n, dic, qtd_criterios, criterios_decisor):
        criterios = {k: v for (v, k) in enumerate(dic.keys())}

        for i in criterios_decisor:
            k = i.criterios[-2:]
            indice = criterios[k]
            el = i.valor * -1
            matriz_n[indice].insert(0, el)

        return matriz_n

    def gerar_matriz(self, qtd_criterios, criterios_decisor):
        ### 1 - gerar matriz base
        matriz_base = []
        for i in range(qtd_criterios):
            matriz_base.append(list(range(1, qtd_criterios + 1)))
        logger.info('Gerar matriz base: {}'.format(matriz_base))

        ### 2 - posicionar zeros na matriz base
        pos_zero = 1
        for lista in matriz_base:
            lista[pos_zero - 1] = 0
            pos_zero += 1

        logger.info('Zeros posicionados na matriz: {}'.format(matriz_base))

        ### 3 - gerar nova matriz com valores positivos após o zero
        # remove os elementos após o 0
        for lista in matriz_base:
            zero_p = lista.index(0)
            for i in lista[zero_p + 1:]:
                lista.remove(i)

        # separa os criterios em um dicionario
        dic_ = collections.OrderedDict()
        for i in range(1, qtd_criterios + 1):
            key = 'c{}'.format(i)
            dic_[key] = []

        for i in criterios_decisor:
            k = i.criterios[:2]
            dic_[k].append(i.valor)

        # completa a matriz com valores positivos
        matriz_com_positivos = self._completa_matriz_com_positivos(matriz_base, dic_, qtd_criterios)

        logger.info('Matriz com valores positivos: {}'.format(matriz_com_positivos))

        ### 4 - gerar nova matriz com valores negativos antes do zero
        matriz_final = self._completa_matriz_com_negativos(matriz_com_positivos, dic_, qtd_criterios, criterios_decisor)

        logger.info('Matriz final: {}'.format(matriz_final))

        return matriz_final

    def gerar_matriz_alt(self, qtd_alternativas, matriz_base, lista_avaliacao):
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

