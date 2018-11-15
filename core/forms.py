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
        fields = ('nome', 'dono', 'decisores')