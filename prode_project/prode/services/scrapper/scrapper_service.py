import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from datetime import datetime

class Scrapper:
    def __init__(self, url):
        """
        Inicializa el scrapper con la URL objetivo.
        """
        self.url = url

    def get_html(self):
        """
        Realiza una solicitud HTTP y devuelve el contenido HTML analizado.
        """
        response = requests.get(self.url)
        response.raise_for_status()
        return BeautifulSoup(response.content, "html.parser")

    def get_matches(self):
        """
        Extrae información de los partidos y equipos desde el HTML.
        """
        soup = self.get_html()

        # Analizar el contenido HTML
        fixture_div = soup.find("div", class_="partidos-content fixture")
        fechas = fixture_div.find_all("div", style=lambda s: s and "display" in s)

        partidos = []
        equipos = set()  # Usamos un set para evitar duplicados

        for fecha in fechas:
            fecha_nombre = fecha.find("div", class_="topnav-fixture").get_text(strip=True)
            partidos_fecha = fecha.find_all("div", class_="partido")

            # Robust fecha_numero extraction
            fecha_parts = fecha_nombre.split(" ")
            if len(fecha_parts) > 1 and fecha_parts[0].lower() == "fecha":  # Case-insensitive check
                try:
                    fecha_numero = int(fecha_parts[1])
                except ValueError:
                    fecha_numero = None
                    print(f"Warning: Invalid fecha number in '{fecha_nombre}'")
            else:
                fecha_numero = None
                print(f"Warning: Could not extract fecha number from '{fecha_nombre}'")

            for partido in partidos_fecha:
                # Extraer equipos y goles
                local = partido.find("div", class_="partido-team local").find("span", class_="partido-name").get_text(strip=True)
                visitante = partido.find("div", class_="partido-team visita").find("span", class_="partido-name").get_text(strip=True)

                goles_local = partido.find("div", class_="partido-score local").find("span", class_="partido-goles").get_text(strip=True)
                
                if goles_local == '-':
                    goles_local = 0
                
                goles_visita = partido.find("div", class_="partido-score visita").find("span", class_="partido-goles").get_text(strip=True)

                if goles_visita == '-':
                    goles_visita = 0

                leyenda = partido.find("div", class_="partido-legend").find("span", class_="date")
                fecha_partido = leyenda.contents[0].strip()
                hora = leyenda.find("span", class_="time").get_text(strip=True) if leyenda.find("span", class_="time") else ""

                # Si no hay hora, agregamos '00:00' por defecto
                if not hora:
                    hora = "00:00"

                estado = leyenda.find("span", class_="timer").get_text(strip=True)

                # Limpiar la hora eliminando el sufijo " HS"
                fecha_str = f"{fecha_partido} {hora}"
                fecha_str = fecha_str.replace(" HS", "")  # Eliminar " HS" de la fecha

                try:
                    # Verificar si la fecha contiene solo la fecha o también la hora
                    if len(fecha_partido.split(" ")) == 1:  # Solo la fecha
                        fecha_str = f"{fecha_partido} 00:00"  # Agregar hora por defecto
                    
                    fecha_obj = datetime.strptime(fecha_str, "%d/%m/%Y %H:%M")
                    fecha_obj = timezone.make_aware(fecha_obj, timezone.get_current_timezone())
                    
                    partidos.append({
                        "Fecha": fecha_nombre,
                        "Local": local,
                        "Visitante": visitante,
                        "Goles Local": goles_local,
                        "Goles Visitante": goles_visita,
                        "Fecha Partido": fecha_partido,
                        "Hora": hora,
                        "Estado": estado,
                        "Fecha Formateada": fecha_obj,  # Esto es lo que guardaremos
                        "Fecha Liga": fecha_numero  # Guardamos solo el número de la fecha (como entero)
                    })
                except ValueError as e:
                    print(f"Error al parsear la fecha: {fecha_str}. Error: {str(e)}")

                # Agregar equipos a la lista sin duplicados
                equipos.add(local)
                equipos.add(visitante)

        return partidos, list(equipos)  # Devolvemos los partidos y los equipos
