import random
import string
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Sum, F
from rest_framework import serializers

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
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predicciones')
    prediccion_local = models.IntegerField()
    prediccion_visitante = models.IntegerField()

    class Meta:
        unique_together = ('partido', 'usuario')  # Evitar duplicados

    def resultado_real(self):
        """Retorna el resultado real del partido como 'L' (Local), 'V' (Visitante), o 'E' (Empate)."""
        if self.partido.goles_local > self.partido.goles_visitante:
            return 'L'  # Victoria del local
        elif self.partido.goles_local < self.partido.goles_visitante:
            return 'V'  # Victoria del visitante
        else:
            return 'E'  # Empate

    def resultado_prediccion(self):
        """Retorna el resultado de la predicción como 'L', 'V', o 'E'."""
        if self.prediccion_local > self.prediccion_visitante:
            return 'L'  # Victoria del local
        elif self.prediccion_local < self.prediccion_visitante:
            return 'V'  # Victoria del visitante
        else:
            return 'E'  # Empate

    def es_correcta(self):
        """Verifica el nivel de acierto y retorna una puntuación según el tipo de acierto."""
        
        puntos = 0  # Puntos totales

        # 1. Acierto exacto (resultado completo)
        if (self.prediccion_local == self.partido.goles_local and
            self.prediccion_visitante == self.partido.goles_visitante):
            puntos += 5  # Acierto completo del resultado con goles 

        # 2. Acierto parcial (goles de un solo equipo)
        elif self.prediccion_local == self.partido.goles_local or self.prediccion_visitante == self.partido.goles_visitante:
            puntos += 1  # Acierto parcial (solo goles de un equipo)

        # 3. Acierto de resultado (1X2)
        if self.resultado_prediccion() == self.resultado_real():
            puntos += 2  # Acierto del resultado (victoria, empate o derrota)

        return puntos  # Retornar la cantidad de puntos obtenidos por la predicción

    def __str__(self):
        return f"{self.usuario} - {self.partido} - {self.prediccion_local}:{self.prediccion_visitante}"

#Grupo de amigos
class Grupo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    privacidad = models.CharField(max_length=10, choices=[('publico', 'Público'), ('privado', 'Privado')])
    creador = models.ForeignKey(User, on_delete=models.CASCADE)
    miembros = models.ManyToManyField(User, related_name="grupos", blank=True)
    codigo_invitacion = models.CharField(max_length=10, unique=True, blank=True, null=True)  
    
    def save(self, *args, **kwargs):
        if not self.codigo_invitacion:
            self.codigo_invitacion = self.generar_codigo_invitacion()
        super(Grupo, self).save(*args, **kwargs)

    @staticmethod
    def generar_codigo_invitacion():
        """Retorna un código de invitación aleatorio para los grupos."""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

    def __str__(self):
        return self.nombre
    
class ChatMessage(models.Model):
    partido = models.ForeignKey('Partido', on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    mensaje = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = '__all__'

class ChatShowMessagesSerializer(serializers.ModelSerializer):
    usuario = serializers.CharField(source='usuario.username', read_only=True)  # Devuelve el nombre de usuario
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'partido', 'usuario', 'mensaje', 'timestamp']