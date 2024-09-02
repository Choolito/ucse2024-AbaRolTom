from django import forms
from .models import Prediccion

class PrediccionForm(forms.ModelForm):
    class Meta:
        model = Prediccion
        fields = ['prediccion_local', 'prediccion_visitante']
