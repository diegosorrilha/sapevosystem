from django import forms
from core.models import *

class NomeProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = ('nome',)


class DecisorForm(forms.ModelForm):
    class Meta:
        model = Decisor
        fields = ('nome',)


class ProjetoForm(forms.ModelForm):
    class Meta:
        model = Projeto
        fields = ('nome', 'decisores')


class AlternativaForm(forms.ModelForm):
    class Meta:
        model = Alternativa
        fields = ('nome',)


class CriterioForm(forms.ModelForm):
    class Meta:
        model = Criterio
        fields = ('nome',)


class AvaliacaoForm(forms.ModelForm):
    class Meta:
        model = Avaliacao
        fields = ('peso',)


class AvaliacaoTempForm(forms.Form):
    FRUIT_CHOICES= [
    ('orange', 'Oranges'),
    ('cantaloupe', 'Cantaloupes'),
    ('mango', 'Mangoes'),
    ('honeydew', 'Honeydews'),
    ]

    COLOR_CHOICES= [
    ('orange', 'Oranges'),
    ('demonio', 'Demonio'),
    ('black', 'Black'),
    ('green', 'Green'),
    ]

    first_name= forms.CharField(max_length=100)
    last_name= forms.CharField(max_length=100)
    favorite_fruit= forms.CharField(label='What is your favorite fruit?', widget=forms.Select(choices=FRUIT_CHOICES))
    email= forms.EmailField()
    age= forms.IntegerField()
    favorite_color= forms.CharField(label='What is your favorite color?', widget=forms.RadioSelect(choices=COLOR_CHOICES))
