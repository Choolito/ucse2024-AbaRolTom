import pdb
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from prode.models import Partido, Prediccion
from prode.forms import PrediccionForm
from django.contrib.auth.decorators import login_required

def lista_partidos(request):
    partidos = Partido.objects.all()

    # Aplicar filtros si se proporcionan
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

    # Si el usuario está logueado, obtener sus predicciones
    predicciones = {}
    if request.user.is_authenticated:
        predicciones_qs = Prediccion.objects.filter(usuario=request.user).values('partido_id', 'prediccion_local', 'prediccion_visitante')
        predicciones = {p['partido_id']: p for p in predicciones_qs}

    context = {
        'partidos': partidos,
        'predicciones': predicciones if request.user.is_authenticated else {}
    }
    return render(request, 'prode/lista_partidos.html', context)

@login_required
def detalle_partido(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)
    usuario = request.user
    
    # Comprobar si el usuario ya ha realizado una predicción para este partido
    prediccion_existente = Prediccion.objects.filter(partido=partido, usuario=usuario).first()

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
        'prediccion_existente': prediccion_existente,
    }
    return render(request, 'prode/detalle_partido.html', context)