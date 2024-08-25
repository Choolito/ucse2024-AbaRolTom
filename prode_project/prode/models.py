from django.db import models
from django.contrib.auth.models import User

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

class Prediccion(models.Model):
    partido = models.ForeignKey(Partido, related_name="predicciones", on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    prediccion_local = models.IntegerField()
    prediccion_visitante = models.IntegerField()

    class Meta:
        unique_together = ('partido', 'usuario')  # Evitar duplicados

    def __str__(self):
        return f"{self.usuario} - {self.partido} - {self.prediccion_local}:{self.prediccion_visitante}"