from django.contrib import admin
from core.models import *

admin.site.register(
    [
        Projeto, 
        Decisor, 
        Alternativa, 
        Criterio, 
        AvaliacaoCriterios,
        AvaliacaoAlternativas,
        PageView,
    ]
)