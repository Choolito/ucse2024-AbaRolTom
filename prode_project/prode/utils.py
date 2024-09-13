import random
import string
from django.contrib.auth.models import User
from django.db.models import Sum, F

from prode.models import Grupo

def calcular_ranking_global():
    """Retorna una lista de usuarios ordenados por puntaje total."""
    
    # Anotar el puntaje total de cada usuario sumando las predicciones correctas
    ranking_global = User.objects.annotate(
        puntaje_total=Sum(F('predicciones__prediccion_local') + F('predicciones__prediccion_visitante'))
    ).order_by('-puntaje_total')
    
    return ranking_global

def calcular_ranking_grupo(grupo_id):
    """Retorna una lista de usuarios ordenados por puntaje total dentro de un grupo."""
    grupo = Grupo.objects.get(id=grupo_id)
    
    # Usuarios del grupo con puntaje acumulado en sus predicciones
    ranking_grupo = grupo.usuarios.annotate(
        puntaje_total=Sum(F('predicciones__prediccion_local') + F('predicciones__prediccion_visitante'))
    ).order_by('-puntaje_total')
    
    return ranking_grupo


def generar_codigo_invitacion():
        """Retorna un codigo de invitacion random para los grupos"""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
