from django.core.management.base import BaseCommand
from prode.models import Equipo, Partido
from prode.services.scrapper.scrapper_service import Scrapper

class Command(BaseCommand):
    help = 'Ejecuta el scrapper para cargar equipos y partidos en la base de datos'

    def handle(self, *args, **kwargs):
        # URL de la página a scrappear
        url = 'https://www.tycsports.com/estadisticas/liga-profesional-de-futbol.html'
        scrapper = Scrapper(url)

        # Cargar equipos
        self.stdout.write("Cargando equipos...")
        partidos, equipos = scrapper.get_matches()
        for equipo_nombre in equipos:
            # Buscar un equipo que coincida con las siglas
            equipo_existente = Equipo.objects.filter(siglas=equipo_nombre).first()

            if not equipo_existente:
                Equipo.objects.get_or_create(
                    nombre=equipo_nombre,
                    siglas=equipo_nombre[:5].upper()  # Asume que las siglas son derivadas del nombre
                )
                self.stdout.write(f"Se cargaron {len(equipos)} equipos.")

        # Cargar partidos
        self.stdout.write("Cargando partidos...")
        for match in partidos:
            try:
                local_team = Equipo.objects.get(siglas=match["Local"])
                visitor_team = Equipo.objects.get(siglas=match["Visitante"])
                Partido.objects.get_or_create(
                    equipo_local=local_team,
                    equipo_visitante=visitor_team,
                    fecha=match["Fecha Formateada"],  # Usamos la fecha formateada
                    goles_local=match["Goles Local"] if match["Goles Local"] else None,
                    goles_visitante=match["Goles Visitante"] if match["Goles Visitante"] else None,
                    status=match["Estado"],
                    fecha_liga=match["Fecha Liga"],
                )
            except Equipo.DoesNotExist:
                self.stdout.write(f"No se encontró el equipo: {match['Local']} o {match['Visitante']}")
        self.stdout.write(f"Se cargaron {len(partidos)} partidos.")
