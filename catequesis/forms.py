from django import forms
from .models import Catequista, GrupoCatequesis, HorarioCatequesis


class CatequistaForm(forms.ModelForm):
    class Meta:
        model = Catequista
        fields = ['nombre']


class GrupoCatequesisForm(forms.ModelForm):
    class Meta:
        model = GrupoCatequesis
        fields = ['numero_grupo', 'catequista', 'lugar', 'dia']


class HorarioCatequesisForm(forms.ModelForm):
    class Meta:
        model = HorarioCatequesis
        fields = ['grupo', 'hora_inicio', 'hora_fin']
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
        }