import pdb
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from prode.models import Partido, Prediccion
from prode.forms import PrediccionForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone

def lista_partidos(request):
    partidos = Partido.objects.all()

    # Aplicar filtros si se proporcionan
    equipo = request.GET.get('equipo')
    fecha = request.GET.get('fecha')
    hora = request.GET.get('hora')
    fecha_liga = request.GET.get('fecha_liga')

    if equipo:
        partidos = partidos.filter(
            Q(equipo_local__nombre__icontains=equipo) | 
            Q(equipo_visitante__nombre__icontains=equipo)
        )
    if fecha:
        partidos = partidos.filter(fecha__date=fecha)
    if hora:
        partidos = partidos.filter(fecha__time__startswith=hora)
    if fecha_liga:
        partidos = partidos.filter(fecha_liga=fecha_liga)

    # Si el usuario está autenticado, buscar sus predicciones
    # Crear un diccionario de predicciones del usuario con el partido.id como clave
    usuario = request.user
    predicciones_usuario = {
        prediccion.partido.id: prediccion 
        for prediccion in Prediccion.objects.filter(usuario=usuario)
    }

    # Crear un diccionario para verificar si el tiempo límite ha pasado para cada partido
    tiempos_limite = {}
    for partido in partidos:
        tiempo_limite = partido.fecha - timezone.timedelta(hours=1)
        if timezone.now() > tiempo_limite:
            tiempos_limite[partido.id] = True

    context = {
        'partidos': partidos,
        'predicciones_usuario': predicciones_usuario,
        'tiempos_limite': tiempos_limite,  
        'rango_fechas': range(1, 28),
    }

    return render(request, 'prode/lista_partidos.html', context)


@login_required
def detalle_partido(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)
    usuario = request.user
    
    # Comprobar si el usuario ya ha realizado una predicción para este partido
    prediccion_existente = Prediccion.objects.filter(partido=partido, usuario=usuario).first()

    # Verificar si la hora del partido - 1 hora es mayor a la hora actual
    tiempo_limite = partido.fecha - timezone.timedelta(hours=1)
    if timezone.now() > tiempo_limite:
        return redirect('lista_partidos')

    if request.method == 'POST':
        if not prediccion_existente:  # Evitar duplicados
            prediccion_local = request.POST.get('prediccion_local')
            prediccion_visitante = request.POST.get('prediccion_visitante')

            Prediccion.objects.create(
                partido=partido,
                usuario=usuario,
                prediccion_local=prediccion_local,
                prediccion_visitante=prediccion_visitante
            )
        return redirect('lista_partidos')

    context = {
        'partido': partido,
        'prediccion_existente': prediccion_existente
    }
    return render(request, 'prode/detalle_partido.html', context)