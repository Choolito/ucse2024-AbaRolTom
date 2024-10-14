import random
import string
from django.contrib.auth.models import User
from django.db.models import Sum, F, Case, When, IntegerField, Value
from prode.models import Grupo

def calcular_ranking_global():
    """Retorna una lista de usuarios ordenados por puntaje total basado en las predicciones de partidos finalizados."""
    
    # Recuperar usuarios
    users = User.objects.all()
    print(f"Usuarios recuperados: {users}")  # Muestra todos los usuarios

    ranking_global = []
    
    for user in users:
        # Filtrar las predicciones del usuario para partidos finalizados
        predicciones = user.predicciones.filter(partido__status='finalizado')
        print(f"Predicciones: {predicciones}")  # Muestra todos los usuarios

        # Calcular el puntaje total utilizando el método es_correcta
        puntaje_total = sum(prediccion.es_correcta() for prediccion in predicciones)
        print (f"puntaje {puntaje_total}")
        ranking_global.append((user, puntaje_total))
    
    # Ordenar el ranking por puntaje total
    ranking_global.sort(key=lambda x: x[1], reverse=True)
    print(ranking_global)
    return ranking_global


def calcular_ranking_grupo(grupo_id):
    """Retorna una lista de usuarios ordenados por puntaje total dentro de un grupo basado en las predicciones de partidos finalizados."""
    
    grupo = Grupo.objects.get(id=grupo_id)
    ranking_grupo = []
    
    for miembro in grupo.miembros.all():
        # Filtrar las predicciones del miembro para partidos finalizados
        predicciones = miembro.predicciones.filter(partido__status='finalizado')
        
        # Calcular el puntaje total utilizando el método es_correcta
        puntaje_total = sum(prediccion.es_correcta() for prediccion in predicciones)
        
        ranking_grupo.append((miembro, puntaje_total))
    
    # Ordenar el ranking por puntaje total
    ranking_grupo.sort(key=lambda x: x[1], reverse=True)
    
    return ranking_grupo
