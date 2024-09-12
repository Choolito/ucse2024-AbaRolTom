import pdb
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from prode.models import Grupo, Partido, Prediccion
from prode.forms import PrediccionForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, F, Q
from prode_project.prode.utils import calcular_ranking_global, calcular_ranking_grupo, generar_codigo_invitacion


def lista_partidos(request):
    # Obtener la fecha actual de la liga
    fecha_liga = request.GET.get('fecha_liga')
    current_fecha = int(fecha_liga) if fecha_liga else 0

    # Asegurarse de que current_fecha esté dentro del rango válido
    current_fecha = max(0, min(current_fecha, 27))

    # Filtrar partidos
    if current_fecha == 0:
        partidos = Partido.objects.all().order_by('fecha_liga', 'fecha')
    else:
        partidos = Partido.objects.filter(fecha_liga=current_fecha).order_by('fecha')

    # Aplicar filtros adicionales si se proporcionan
    equipo = request.GET.get('equipo')
    fecha = request.GET.get('fecha')
    hora = request.GET.get('hora')

    if equipo:
        partidos = partidos.filter(
            Q(equipo_local__nombre__icontains=equipo) | 
            Q(equipo_visitante__nombre__icontains=equipo)
        )
    if fecha:
        partidos = partidos.filter(fecha__date=fecha)
    if hora:
        partidos = partidos.filter(fecha__time__startswith=hora)

    # Si el usuario está autenticado, buscar sus predicciones
    usuario = request.user
    predicciones_usuario = {}
    if usuario.is_authenticated:
        predicciones_usuario = {
            prediccion.partido.id: prediccion 
            for prediccion in Prediccion.objects.filter(usuario=usuario, partido__in=partidos)
        }

    # Crear un diccionario para verificar si el tiempo límite ha pasado para cada partido
    tiempos_limite = {}
    ahora = timezone.now()
    for partido in partidos:
        tiempo_limite = partido.fecha - timezone.timedelta(hours=1)
        if ahora > tiempo_limite:
            tiempos_limite[partido.id] = True
        
        # Actualizar el estado del partido
        tiempo_restante = (partido.fecha - ahora).total_seconds() / 60
        if tiempo_restante > 60:
            partido.status = 'Programado'
        elif tiempo_restante > 0:
            partido.status = 'Por comenzar'
        elif tiempo_restante > -105:
            partido.status = 'En juego'
        else:
            partido.status = 'Finalizado'

    # Calcular fecha anterior y siguiente
    fecha_anterior = max(0, current_fecha - 1)
    fecha_siguiente = min(27, current_fecha + 1)

    context = {
        'partidos': partidos,
        'predicciones_usuario': predicciones_usuario,
        'tiempos_limite': tiempos_limite,  
        'rango_fechas': range(1, 28),
        'current_fecha': current_fecha,
        'fecha_anterior': fecha_anterior,
        'fecha_siguiente': fecha_siguiente,
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

@login_required
def ranking_global(request):
    # Obtener el ranking global
    usuarios_con_puntaje = calcular_ranking_global()

    context = {
        'usuarios_con_puntaje': usuarios_con_puntaje,
    }
    return render(request, 'prode/ranking_global.html', context)

@login_required
def crear_grupo(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre_grupo')
        descripcion = request.POST.get('descripcion_grupo', '')
        privacidad = request.POST.get('privacidad_grupo', 'publico')

        # Crear el grupo con el usuario actual como creador
        grupo = Grupo.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            privacidad=privacidad,
            creador=request.user  # Suponiendo que la relación está en el modelo
        )
        return redirect('detalle_grupo', grupo_id=grupo.id)

    return render(request, 'prode/crear_grupo.html')

@login_required
def unirse_grupo(request):
    if request.method == 'POST':
        codigo_invitacion = request.POST.get('codigo_invitacion')
        
        # Buscar el grupo con ese código de invitación
        grupo = get_object_or_404(Grupo, codigo_invitacion=codigo_invitacion)
        
        # Añadir al usuario al grupo si aún no está
        if request.user not in grupo.miembros.all():
            grupo.miembros.add(request.user)
            return redirect('detalle_grupo', grupo_id=grupo.id)
        else:
            return redirect('')  # Redirigir a la home

    return render(request, 'prode/unirse_grupo.html')

@login_required
def ranking_grupo(request, grupo_id):
    grupo = get_object_or_404(Grupo, id=grupo_id)
    ranking = calcular_ranking_grupo(grupo_id)
    
    context = {
        'grupo': grupo,
        'ranking': ranking,
    }
    return render(request, 'prode/ranking_grupo.html', context)

@login_required
def estadisticas_view(request):
    partidos = Partido.objects.filter(fecha__gt=timezone.now())  # Solo partidos futuros
    estadisticas = []

    for partido in partidos:
        total_predicciones = Prediccion.objects.filter(partido=partido).count()
        
        if total_predicciones == 0:
            porcentaje_victoria_local = porcentaje_victoria_visitante = porcentaje_empate = 0
        else:
            predicciones_local = Prediccion.objects.filter(partido=partido, prediccion_local__gt=F('prediccion_visitante')).count()
            predicciones_visitante = Prediccion.objects.filter(partido=partido, prediccion_visitante__gt=F('prediccion_local')).count()
            predicciones_empate = Prediccion.objects.filter(partido=partido, prediccion_local=F('prediccion_visitante')).count()

            porcentaje_victoria_local = (predicciones_local / total_predicciones) * 100
            porcentaje_victoria_visitante = (predicciones_visitante / total_predicciones) * 100
            porcentaje_empate = (predicciones_empate / total_predicciones) * 100
        
        estadisticas.append({
            'partido': partido,
            'porcentaje_victoria_local': porcentaje_victoria_local,
            'porcentaje_victoria_visitante': porcentaje_victoria_visitante,
            'porcentaje_empate': porcentaje_empate
        })

    context = {
        'estadisticas': estadisticas,
    }
    return render(request, 'prode/estadisticas.html', context)