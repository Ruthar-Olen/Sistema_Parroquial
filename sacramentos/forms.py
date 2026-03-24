from django import forms
from .models import Inscripcion
from catequesis.models import GrupoCatequesis


class InscripcionForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        exclude = ['horario_catequesis', 'nombre_novio']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),

            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control'}),

            'nombre_padre': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_madre': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_padrino': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_madrina': forms.TextInput(attrs={'class': 'form-control'}),

            'catequista': forms.Select(attrs={'class': 'form-control'}),
            'grupo_catequesis': forms.Select(attrs={'class': 'form-control'}),

            'lugar_clases': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'dia_clases': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'hora_clases': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),

            'otros_documentos': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['grupo_catequesis'].queryset = GrupoCatequesis.objects.none()

        if self.instance.pk and self.instance.catequista:
            self.fields['grupo_catequesis'].queryset = GrupoCatequesis.objects.filter(
                catequista=self.instance.catequista
            ).order_by('numero_grupo')

        # Quitar "Matrimonio" del select de tipo
        if 'tipo' in self.fields:
            self.fields['tipo'].choices = [
                choice for choice in self.fields['tipo'].choices
                if str(choice[0]).lower() != 'matrimonio'
            ]