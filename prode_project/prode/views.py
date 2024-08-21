from django.shortcuts import get_object_or_404, render
from django.db.models import Q
from prode.models import Partido

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

    context = {
        'partidos': partidos
    }
    return render(request, 'prode/lista_partidos.html', context)

def detalle_partido(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)

    if request.method == 'POST':
        # Aquí puedes agregar lógica para guardar la predicción
        prediccion_local = request.POST.get('prediccion_local')
        prediccion_visitante = request.POST.get('prediccion_visitante')
        # Guardar la predicción en la base de datos o realizar otra acción

    context = {
        'partido': partido
    }
    return render(request, 'prode/detalle_partido.html', context)