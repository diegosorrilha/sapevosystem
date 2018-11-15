from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from core.forms import DecisorForm, ProjetoForm, NomeProjetoForm
from core.models import Projeto


def index(request):
    """ 
    1 - cadastrar somente nome do projeto e redirecionar para cadastrar decisores - OK
    2 - cadastrar decisores
    3 - atualizar cadastro do projeto com decisores
    4 - cadastra Alternativas
    5 - cadastra Criterios
    6 - cadastra Peso
    7 - avalia Critérios
    8 - coloca resultado final da avaliação no projeto
    """
    template_name = 'index.html'

    if request.method == "POST":
        nome_projeto_form = NomeProjetoForm(request.POST)
        if nome_projeto_form.is_valid():
            nome_projeto_form.save()

        return HttpResponseRedirect('/view_temp/')

    else:
        nome_projeto_form = NomeProjetoForm()

    return render(request, template_name, {'nome_projeto_form': nome_projeto_form})


def view_temp(request):
    print('entrou na view temp')
    template_name = 'index.html'

    dados = Projeto.objects.all()

    return render(request, template_name, {'dados': dados})




def cadastra_decisores(request):
    template_name = 'index.html'
    projeto_form = ProjetoForm(request.POST)
        
    return render(request, template_name, {'projeto_form': projeto_form,})


def atualiza_projeto_com_decisores(request):
    pass


def cadastra_alternativas(request):
    pass


def cadastra_criterios(request):
    pass


def cadastra_peso(request):
    pass


def avalia_criterios(request):
    pass

# multiplos forms
# form = MyFormClass(prefix='some_prefix')
# and then, as long as the prefix is the same, process data as:

# form = MyFormClass(request.POST, prefix='some_prefix')


# >>> novo = Decisor(nome='Diego')
# >>> novo.save()
# >>> novo_2 = Decisor(nome='Luiz')
# >>> novo_2.save()
# >>> pp = Projeto(nome='eita nois', dono=novo)
# >>> pp.save()
# >>> pp.decisores.add(novo, novo_2)
# >>> ps = Projeto.objects.all()
# >>> for i in ps[2].decisores.all():
# ...     print(i.nome)
# ...
# Diego
# Luiz
# >>>