from django.db import models  # Importa herramientas para crear modelos en Django
from django.core.exceptions import ValidationError  # Importa error de validación para reglas personalizadas


class Catequista(models.Model):
    nombre = models.CharField(max_length=150)  # Nombre completo del catequista

    class Meta:
        verbose_name = 'Catequista'  # Nombre singular visible en admin
        verbose_name_plural = 'Catequistas'  # Nombre plural visible en admin
        ordering = ['nombre']  # Ordena alfabéticamente por nombre

    def __str__(self):
        return self.nombre  # Devuelve el nombre del catequista


class GrupoCatequesis(models.Model):
    numero_grupo = models.CharField(max_length=20)  # Número o clave del grupo, por ejemplo 1A o 3C
    catequista = models.ForeignKey(
        Catequista,
        on_delete=models.CASCADE,
        related_name='grupos'
    )  # Catequista responsable del grupo
    lugar = models.CharField(max_length=150)  # Lugar donde se imparte la catequesis
    dia = models.CharField(max_length=50)  # Día en que se reúne el grupo

    class Meta:
        verbose_name = 'Grupo de catequesis'  # Nombre singular visible en admin
        verbose_name_plural = 'Grupos de catequesis'  # Nombre plural visible en admin
        ordering = ['numero_grupo']  # Ordena por número de grupo

    def __str__(self):
        return f"{self.numero_grupo} - {self.catequista.nombre} - {self.dia}"
        # Devuelve una representación legible del grupo


class HorarioCatequesis(models.Model):
    grupo = models.ForeignKey(
        GrupoCatequesis,
        on_delete=models.CASCADE,
        related_name='horarios'
    )  # Grupo al que pertenece este horario
    hora_inicio = models.TimeField()  # Hora de inicio de la sesión
    hora_fin = models.TimeField()  # Hora de fin de la sesión

    class Meta:
        verbose_name = 'Horario de catequesis'  # Nombre singular visible en admin
        verbose_name_plural = 'Horarios de catequesis'  # Nombre plural visible en admin
        ordering = ['grupo__numero_grupo', 'hora_inicio']  # Ordena por grupo y hora de inicio

    def __str__(self):
        return f"{self.grupo.numero_grupo} - {self.hora_inicio.strftime('%H:%M')} a {self.hora_fin.strftime('%H:%M')}"
        # Devuelve una representación legible del horario


class FormatoTipo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)  # Nombre visible del tipo de formato
    clave = models.CharField(max_length=30, unique=True)  # Clave interna única del tipo de formato
    activo = models.BooleanField(default=True)  # Permite activar o desactivar tipos sin borrarlos

    class Meta:
        verbose_name = 'Tipo de formato'  # Nombre singular visible en admin
        verbose_name_plural = 'Tipos de formato'  # Nombre plural visible en admin
        ordering = ['nombre']  # Ordena alfabéticamente por nombre

    def __str__(self):
        return self.nombre  # Devuelve el nombre del tipo de formato


class FormatoCatequesis(models.Model):
    ORIENTACION_VERTICAL = 'vertical'  # Valor interno para orientación vertical
    ORIENTACION_HORIZONTAL = 'horizontal'  # Valor interno para orientación horizontal

    ORIENTACION_CHOICES = [
        (ORIENTACION_VERTICAL, 'Vertical'),  # Opción visible vertical
        (ORIENTACION_HORIZONTAL, 'Horizontal'),  # Opción visible horizontal
    ]  # Opciones permitidas para la orientación del documento

    tipo = models.ForeignKey(
        FormatoTipo,
        on_delete=models.PROTECT,
        related_name='formatos'
    )  # Tipo de formato al que pertenece este registro

    ciclo = models.CharField(max_length=20)  # Ciclo del formato, por ejemplo 2025-2026
    titulo = models.CharField(max_length=255)  # Título principal del formato
    subtitulo = models.CharField(max_length=255, blank=True)  # Subtítulo opcional del formato
    texto_pie = models.TextField(blank=True)  # Texto inferior visible en el documento
    orientacion = models.CharField(
        max_length=20,
        choices=ORIENTACION_CHOICES,
        default=ORIENTACION_VERTICAL
    )  # Orientación del documento, vertical u horizontal

    activo = models.BooleanField(default=False)  # Indica si este formato es el vigente para su tipo
    usa_celdas = models.BooleanField(default=True)  # Indica si el formato usa cuadrícula editable
    fecha_creacion = models.DateTimeField(auto_now_add=True)  # Fecha de creación automática
    fecha_actualizacion = models.DateTimeField(auto_now=True)  # Fecha de actualización automática

    class Meta:
        verbose_name = 'Formato de catequesis'  # Nombre singular visible en admin
        verbose_name_plural = 'Formatos de catequesis'  # Nombre plural visible en admin
        ordering = ['tipo__nombre', '-ciclo', '-fecha_creacion']  # Ordena por tipo y después por ciclo reciente
        unique_together = ('tipo', 'ciclo', 'titulo')  # Evita duplicados exactos por tipo, ciclo y título

    def __str__(self):
        return f'{self.tipo.nombre} - {self.ciclo} - {self.titulo}'
        # Devuelve una representación legible del formato

    def clean(self):
        if self.activo:
            formato_activo_existente = FormatoCatequesis.objects.filter(
                tipo=self.tipo,
                activo=True
            ).exclude(pk=self.pk)
            # Busca otro formato activo del mismo tipo
            # Excluye el propio registro si ya existe

            if formato_activo_existente.exists():
                raise ValidationError('Ya existe un formato activo para este tipo.')
                # Impide que existan dos formatos activos del mismo tipo al mismo tiempo

    def save(self, *args, **kwargs):
        self.full_clean()
        # Ejecuta validaciones del modelo antes de guardar

        super().save(*args, **kwargs)
        # Guarda normalmente el objeto en la base de datos


class FormatoCelda(models.Model):
    formato = models.ForeignKey(
        FormatoCatequesis,
        on_delete=models.CASCADE,
        related_name='celdas'
    )  # Formato al que pertenece esta celda

    fila = models.PositiveIntegerField()  # Número de fila de la celda
    columna = models.PositiveIntegerField()  # Número de columna de la celda
    contenido = models.CharField(max_length=255, blank=True)  # Texto visible dentro de la celda
    destacado = models.BooleanField(default=False)  # Permite marcar celdas especiales si luego se requiere
    orden = models.PositiveIntegerField(default=0)  # Campo auxiliar por si luego quieres ordenar manualmente

    class Meta:
        verbose_name = 'Celda del formato'  # Nombre singular visible en admin
        verbose_name_plural = 'Celdas del formato'  # Nombre plural visible en admin
        ordering = ['fila', 'columna', 'orden']  # Ordena por posición natural dentro de la cuadrícula
        unique_together = ('formato', 'fila', 'columna')  # Evita repetir una misma posición en el formato

    def __str__(self):
        return f'{self.formato.titulo} - F{self.fila} C{self.columna}'
        # Devuelve una representación legible de la celda