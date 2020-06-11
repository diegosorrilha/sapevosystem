import logging

logger = logging.getLogger(__name__)

"""
- talvez separa classe Calcula para uma classe Peso
- - Peso.calcular_peso_criterios (views.py: 366)
"""


class Calculo:

    def _separa_elementos(self, lista_elementos, idx):
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

    def get_peso_criterios(self, lista_elementos):
        num_elementos = len(lista_elementos[0])

        soma_pesos = []
        for idx in range(num_elementos):
            lista_temp = []
            lista_temp = self._separa_elementos(lista_elementos, idx)
            soma_pesos.append(sum(lista_temp))

        return soma_pesos
