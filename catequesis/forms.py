from django import forms  # Importa herramientas para crear formularios Django
from .models import (
    Catequista,
    GrupoCatequesis,
    HorarioCatequesis,
    FormatoCatequesis,
)  # Importa los modelos del módulo catequesis


class CatequistaForm(forms.ModelForm):
    class Meta:
        model = Catequista  # Indica qué modelo usa este formulario
        fields = ['nombre']  # Campo visible del formulario


class GrupoCatequesisForm(forms.ModelForm):
    class Meta:
        model = GrupoCatequesis  # Indica qué modelo usa este formulario
        fields = ['numero_grupo', 'catequista', 'lugar', 'dia']  # Campos visibles del formulario


class HorarioCatequesisForm(forms.ModelForm):
    class Meta:
        model = HorarioCatequesis  # Indica qué modelo usa este formulario
        fields = ['grupo', 'hora_inicio', 'hora_fin']  # Campos visibles del formulario
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),  # Input tipo hora para hora de inicio
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),  # Input tipo hora para hora de fin
        }  # Define widgets personalizados


class FormatoCatequesisForm(forms.ModelForm):
    class Meta:
        model = FormatoCatequesis  # Indica qué modelo usa este formulario
        fields = [
            'tipo',  # Tipo de formato, por ejemplo Niño, Papás o Tarjetón
            'ciclo',  # Ciclo del formato, por ejemplo 2026-2027
            'titulo',  # Primera línea del encabezado
            'subtitulo',  # Segunda línea del encabezado
            'texto_pie',  # Texto inferior del formato
            'orientacion',  # Orientación del documento
            'activo',  # Indica si el formato está vigente
            'usa_celdas',  # Indica si el formato utiliza cuadrícula editable
        ]  # Campos visibles del formulario

        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-control'}),  # Selector del tipo de formato
            'ciclo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: 2026-2027'
            }),  # Campo de texto para el ciclo
            'titulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Parroquia de la Santísima Trinidad'
            }),  # Campo para la primera línea del encabezado
            'subtitulo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: Capilla del Señor de la Misericordia 2026-2027'
            }),  # Campo para la segunda línea del encabezado
            'texto_pie': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Texto inferior del formato'
            }),  # Área de texto para el pie del formato
            'orientacion': forms.Select(attrs={'class': 'form-control'}),  # Selector de orientación
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),  # Check para activar formato
            'usa_celdas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),  # Check para usar cuadrícula
        }  # Define widgets personalizados

        labels = {
            'tipo': 'Tipo de formato',  # Etiqueta del tipo
            'ciclo': 'Ciclo',  # Etiqueta del ciclo
            'titulo': 'Título principal',  # Etiqueta de la primera línea
            'subtitulo': 'Subtítulo / sede',  # Etiqueta de la segunda línea
            'texto_pie': 'Texto del pie',  # Etiqueta del pie
            'orientacion': 'Orientación',  # Etiqueta de orientación
            'activo': 'Formato activo',  # Etiqueta de activo
            'usa_celdas': 'Usa cuadrícula editable',  # Etiqueta de uso de celdas
        }  # Etiquetas visibles del formulario