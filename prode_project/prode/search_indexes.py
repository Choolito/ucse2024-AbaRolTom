# search_indexes.py
from haystack import indexes
from .models import Equipo, Partido

class EquipoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    nombre = indexes.CharField(model_attr='nombre')
    
    def get_model(self):
        return Equipo
    
    def index_queryset(self, using=None):
        """Usado cuando el índice es actualizado."""
        return self.get_model().objects.all()

class PartidoIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.EdgeNgramField(document=True, use_template=True)
    equipo_local = indexes.CharField(model_attr='equipo_local__nombre')
    equipo_visitante = indexes.CharField(model_attr='equipo_visitante__nombre')
    fecha = indexes.DateTimeField(model_attr='fecha_liga')

    def get_model(self):
        return Partido
    
    def index_queryset(self, using=None):
        """Usado cuando el índice es actualizado."""
        return self.get_model().objects.all()
