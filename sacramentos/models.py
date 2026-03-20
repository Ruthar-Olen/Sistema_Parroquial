from django.db import models


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

    lugar_clases = models.CharField(max_length=150, blank=True, null=True)
    dia_clases = models.CharField(max_length=50, blank=True, null=True)
    hora_clases = models.CharField(max_length=50, blank=True, null=True)

    bautizo = models.BooleanField(default=False)
    eucaristia = models.BooleanField(default=False)
    confirmacion = models.BooleanField(default=False)
    matrimonio = models.BooleanField(default=False)

    acta_nacimiento = models.BooleanField(default=False)
    boleta_bautizo = models.BooleanField(default=False)
    boleta_confirmacion = models.BooleanField(default=False)
    ine = models.BooleanField(default=False)
    otros_documentos = models.CharField(max_length=255, blank=True, null=True)

    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_completo} - {self.get_tipo_display()}"