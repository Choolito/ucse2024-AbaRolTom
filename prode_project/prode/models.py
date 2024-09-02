from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Equipo(models.Model):
    nombre = models.CharField(max_length=100)
    escudo = models.ImageField(upload_to='escudos/', null=True, blank=True)
    
    def __str__(self):
        return str(self.nombre)


class Partido(models.Model):
    equipo_local = models.ForeignKey(Equipo, related_name='local', on_delete=models.CASCADE)
    equipo_visitante = models.ForeignKey(Equipo, related_name='visitante', on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    goles_local = models.IntegerField(blank=True, null=True)
    goles_visitante = models.IntegerField(blank=True, null=True)
    fecha_liga = models.IntegerField(blank=True, null=True)

    STATUS_CHOICES = [
        ('programado', 'Programado'),
        ('por_comenzar', 'Por comenzar'),
        ('en_proceso', 'En proceso'),
        ('suspendido', 'Suspendido'),
        ('cancelado', 'Cancelado'),
        ('finalizado', 'Finalizado'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='programado')

    def get_status_display(self):
        ahora = timezone.now()
        tiempo_restante = (self.fecha - ahora).total_seconds() / 60

        if tiempo_restante > 60:
            return 'Programado'
        elif tiempo_restante > 0:
            return 'Por comenzar'
        elif tiempo_restante > -105:
            return 'En juego'
        else:
            return 'Finalizado'
        
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