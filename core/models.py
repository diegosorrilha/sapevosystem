from django.db import models

class Decisor(models.Model):
    projeto = models.ForeignKey('Projeto', on_delete=models.CASCADE, null=True)
    nome = models.CharField(max_length=20)
    avaliou_criterios = models.BooleanField(default=False)
    avaliou_alternativas = models.BooleanField(default=False)

    def __str__(self):
        return self.nome


class Projeto(models.Model):
    nome = models.CharField(max_length=20)
    decisores = models.ManyToManyField('Decisor', related_name='+')
    # resultado_avaliacao = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class Alternativa(models.Model):
    projeto = models.ForeignKey('Projeto', on_delete=models.CASCADE, null=True)
    nome = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class Criterio(models.Model):
    projeto = models.ForeignKey('Projeto', on_delete=models.CASCADE, null=True)
    nome = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class Peso(models.Model):
    codigo = models.CharField(max_length=20)
    description = models.CharField(max_length=20)
    valor = models.IntegerField()


class AvaliacaoCriterios(models.Model):
    projeto = models.ForeignKey('Projeto', on_delete=models.CASCADE)
    decisor = models.ForeignKey('Decisor', on_delete=models.CASCADE)
    criterios = models.CharField(max_length=20)
    valor = models.IntegerField()

    def __str__(self):
        return f'{self.decisor} - {self.criterios}'