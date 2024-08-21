from django.db import models

class Equipo(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return str(self.nombre)


class Partido(models.Model):
    equipo_local = models.ForeignKey(Equipo, related_name='local', on_delete=models.CASCADE)
    equipo_visitante = models.ForeignKey(Equipo, related_name='visitante', on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    goles_local = models.IntegerField(blank=True, null=True)
    goles_visitante = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.equipo_local} vs {self.equipo_visitante} - {self.fecha}"