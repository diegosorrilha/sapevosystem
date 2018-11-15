from django.db import models

class Decisor(models.Model):
    nome = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class Projeto(models.Model):
    nome = models.CharField(max_length=20)
    dono = models.ForeignKey('Decisor', on_delete=models.CASCADE, default=1)
    decisores = models.ManyToManyField('Decisor', related_name='+')
    # resultado_avaliacao = models.CharField(max_length=20)

    def __str__(self):
        return self.nome


class Alternativa(models.Model):
    projeto = models.ForeignKey('Projeto', on_delete=models.CASCADE)
    titulo = models.TextField()


class Criterio(models.Model):
    projeto = models.ForeignKey('Projeto', on_delete=models.CASCADE)
    titulo = models.TextField()


class Peso(models.Model):
    codigo = models.TextField()
    description = models.TextField()
    valor = models.IntegerField()


class Avaliacao(models.Model):
    projeto = models.ForeignKey('Projeto', on_delete=models.CASCADE)
    decisor = models.ForeignKey('Decisor', on_delete=models.CASCADE)
    alternativa = models.ForeignKey('Alternativa', on_delete=models.CASCADE)
    criterio = models.ForeignKey('Criterio', on_delete=models.CASCADE)
    peso = models.ForeignKey('Peso', on_delete=models.CASCADE)



# para classe de valores_pesos
# class Student(models.Model):
#     FRESHMAN = 'FR'
#     SOPHOMORE = 'SO'
#     JUNIOR = 'JR'
#     SENIOR = 'SR'
#     YEAR_IN_SCHOOL_CHOICES = (
#         (FRESHMAN, 'Freshman'),
#         (SOPHOMORE, 'Sophomore'),
#         (JUNIOR, 'Junior'),
#         (SENIOR, 'Senior'),
#     )
#     year_in_school = models.CharField(
#         max_length=2,
#         choices=YEAR_IN_SCHOOL_CHOICES,
#         default=FRESHMAN,
    # )