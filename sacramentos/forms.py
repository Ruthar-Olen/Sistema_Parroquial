from django import forms
from .models import Inscripcion


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

            'lugar_clases': forms.TextInput(attrs={'class': 'form-control'}),
            'dia_clases': forms.TextInput(attrs={'class': 'form-control'}),
            'hora_clases': forms.TextInput(attrs={'class': 'form-control'}),

            'otros_documentos': forms.TextInput(attrs={'class': 'form-control'}),
        }