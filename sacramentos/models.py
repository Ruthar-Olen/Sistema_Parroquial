from django.db import models
from catequesis.models import Catequista, GrupoCatequesis, HorarioCatequesis


class Inscripcion(models.Model):
    TIPO_CHOICES = [
        ('comunion', 'Primera Comunión'),
        ('confirmacion', 'Confirmación'),
        ('matrimonio', 'Matrimonio'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha = models.DateField()

    nombre_completo = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    edad = models.PositiveIntegerField(blank=True, null=True)

    nombre_padre = models.CharField(max_length=255, blank=True, null=True)
    nombre_madre = models.CharField(max_length=255, blank=True, null=True)
    nombre_novio = models.CharField(max_length=255, blank=True, null=True)
    nombre_padrino = models.CharField(max_length=255, blank=True, null=True)
    nombre_madrina = models.CharField(max_length=255, blank=True, null=True)

    # Relación con catequesis
    catequista = models.ForeignKey(Catequista, on_delete=models.SET_NULL, null=True, blank=True)
    grupo_catequesis = models.ForeignKey(GrupoCatequesis, on_delete=models.SET_NULL, null=True, blank=True)
    horario_catequesis = models.ForeignKey(HorarioCatequesis, on_delete=models.SET_NULL, null=True, blank=True)

    # Datos autocompletados desde catequesis
    lugar_clases = models.CharField(max_length=150, blank=True, null=True)
    dia_clases = models.CharField(max_length=50, blank=True, null=True)
    hora_clases = models.CharField(max_length=50, blank=True, null=True)

    # Historial sacramental
    bautizo = models.BooleanField(default=False)
    eucaristia = models.BooleanField(default=False)
    confirmacion = models.BooleanField(default=False)
    matrimonio = models.BooleanField(default=False)

    # Documentos
    acta_nacimiento = models.BooleanField(default=False)
    boleta_bautizo = models.BooleanField(default=False)
    boleta_confirmacion = models.BooleanField(default=False)
    ine = models.BooleanField(default=False)
    otros_documentos = models.CharField(max_length=255, blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_completo} - {self.get_tipo_display()}"