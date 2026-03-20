from django import forms
from .models import Inscripcion
from catequesis.models import GrupoCatequesis, HorarioCatequesis


class InscripcionForm(forms.ModelForm):
    class Meta:
        model = Inscripcion
        fields = '__all__'
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),

            'nombre_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control'}),

            'nombre_padre': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_madre': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_novio': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_padrino': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre_madrina': forms.TextInput(attrs={'class': 'form-control'}),

            'catequista': forms.Select(attrs={'class': 'form-control'}),
            'grupo_catequesis': forms.Select(attrs={'class': 'form-control'}),
            'horario_catequesis': forms.Select(attrs={'class': 'form-control'}),

            'lugar_clases': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'dia_clases': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'hora_clases': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),

            'otros_documentos': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['grupo_catequesis'].queryset = GrupoCatequesis.objects.none()
        self.fields['horario_catequesis'].queryset = HorarioCatequesis.objects.none()

        if self.instance.pk:
            if self.instance.catequista:
                self.fields['grupo_catequesis'].queryset = GrupoCatequesis.objects.filter(
                    catequista=self.instance.catequista
                ).order_by('numero_grupo')

            if self.instance.grupo_catequesis:
                self.fields['horario_catequesis'].queryset = HorarioCatequesis.objects.filter(
                    grupo=self.instance.grupo_catequesis
                ).order_by('hora_inicio')