from django import forms  # Importa herramientas para formularios Django
from .models import BienInventario, AreaInventario, EstadoInventario  # Importa los modelos del módulo


class BienInventarioForm(forms.ModelForm):
    class Meta:
        model = BienInventario  # Indica qué modelo usa este formulario
        fields = [
            'area',  # Área donde se ubica el bien
            'descripcion',  # Descripción del bien
            'cantidad',  # Cantidad
            'estado',  # Estado actual del bien
            'observaciones',  # Comentarios adicionales
            'fotografia',  # Imagen del bien
        ]  # Campos visibles del formulario

        widgets = {
            'area': forms.Select(attrs={'class': 'form-control'}),  # Selector de área
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe el bien de manera clara y específica'
            }),  # Área de texto para descripción
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),  # Campo numérico para cantidad
            'estado': forms.Select(attrs={'class': 'form-control'}),  # Selector de estado
            'observaciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Observaciones opcionales'
            }),  # Área de texto para observaciones
            'fotografia': forms.ClearableFileInput(attrs={'class': 'form-control'}),  # Campo para subir imagen
        }  # Define widgets personalizados

        labels = {
            'area': 'Área',  # Etiqueta del área
            'descripcion': 'Descripción del bien',  # Etiqueta descripción
            'cantidad': 'Cantidad',  # Etiqueta cantidad
            'estado': 'Estado del bien',  # Etiqueta estado
            'observaciones': 'Comentario / observaciones',  # Etiqueta observaciones
            'fotografia': 'Fotografía del bien',  # Etiqueta foto
        }  # Etiquetas visibles

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # Inicializa el formulario base

        self.fields['area'].queryset = AreaInventario.objects.filter(activa=True).order_by('nombre')  
        # Muestra solo áreas activas y ordenadas por nombre

        self.fields['estado'].queryset = EstadoInventario.objects.filter(activo=True).order_by('nombre')  
        # Muestra solo estados activos y ordenados por nombre