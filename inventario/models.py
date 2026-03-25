from django.db import models  # Importa herramientas para crear modelos en Django
from django.utils import timezone  # Importa utilidades de fecha y hora


class AreaInventario(models.Model):
    nombre = models.CharField(max_length=150, unique=True)  # Nombre completo del área
    prefijo = models.CharField(max_length=10, unique=True)  # Prefijo corto usado para generar el código
    activa = models.BooleanField(default=True)  # Permite activar o desactivar áreas sin borrarlas

    class Meta:
        verbose_name = 'Área de inventario'  # Nombre singular visible en admin
        verbose_name_plural = 'Áreas de inventario'  # Nombre plural visible en admin
        ordering = ['nombre']  # Ordena alfabéticamente por nombre

    def __str__(self):
        return f'{self.nombre} ({self.prefijo})'  # Representación legible del área


class EstadoInventario(models.Model):
    nombre = models.CharField(max_length=100, unique=True)  # Nombre del estado del bien
    activo = models.BooleanField(default=True)  # Permite ocultar estados sin borrarlos

    class Meta:
        verbose_name = 'Estado del inventario'  # Nombre singular visible en admin
        verbose_name_plural = 'Estados del inventario'  # Nombre plural visible en admin
        ordering = ['nombre']  # Orden alfabético

    def __str__(self):
        return self.nombre  # Devuelve el nombre del estado


class BienInventario(models.Model):
    codigo = models.CharField(max_length=30, unique=True, blank=True)  # Código automático del bien
    prefijo_area = models.CharField(max_length=10, blank=True)  # Guarda el prefijo del área para referencia interna

    area = models.ForeignKey(
        AreaInventario,
        on_delete=models.PROTECT,
        related_name='bienes'
    )  # Área a la que pertenece el bien

    descripcion = models.TextField()  # Descripción detallada del bien
    cantidad = models.PositiveIntegerField(default=1)  # Cantidad del bien
    estado = models.ForeignKey(
        EstadoInventario,
        on_delete=models.PROTECT,
        related_name='bienes'
    )  # Estado actual del bien

    observaciones = models.TextField(blank=True)  # Comentarios adicionales
    fotografia = models.ImageField(
        upload_to='inventario/',
        blank=True,
        null=True
    )  # Fotografía opcional del bien

    activo = models.BooleanField(default=True)  # Sirve para saber si el bien sigue activo o fue dado de baja
    fecha_alta = models.DateTimeField(default=timezone.now)  # Fecha de alta del bien
    fecha_actualizacion = models.DateTimeField(auto_now=True)  # Fecha de última actualización automática

    class Meta:
        verbose_name = 'Bien de inventario'  # Nombre singular visible en admin
        verbose_name_plural = 'Bienes de inventario'  # Nombre plural visible en admin
        ordering = ['-fecha_alta', 'codigo']  # Orden por fecha más reciente y luego código

    def __str__(self):
        return f'{self.codigo} - {self.descripcion}'  # Representación legible del bien

    def generar_codigo(self):
        prefijo = self.area.prefijo.strip().upper()  # Toma el prefijo del área y lo normaliza
        self.prefijo_area = prefijo  # Guarda el prefijo en el campo interno

        fecha_base = self.fecha_alta or timezone.now()  # Usa la fecha de alta si existe, si no la fecha actual
        anio_mes = fecha_base.strftime('%Y%m')  # Convierte la fecha al formato AAAAMM

        bienes_mismo_periodo = BienInventario.objects.filter(
            prefijo_area=prefijo,
            fecha_alta__year=fecha_base.year,
            fecha_alta__month=fecha_base.month
        ).exclude(pk=self.pk)
        # Busca otros bienes del mismo prefijo y mismo año/mes
        # Excluye el propio registro si ya existe

        consecutivo = bienes_mismo_periodo.count() + 1  # Calcula el siguiente consecutivo
        consecutivo_formateado = f'{consecutivo:03d}'  # Lo convierte a tres dígitos: 001, 002, etc.

        return f'{prefijo}-{anio_mes}-{consecutivo_formateado}'
        # Devuelve el código final en el formato definido

    def save(self, *args, **kwargs):
        if not self.fecha_alta:
            self.fecha_alta = timezone.now()
            # Asegura que exista fecha de alta antes de generar el código

        if not self.codigo:
            self.codigo = self.generar_codigo()
            # Si aún no tiene código, lo genera automáticamente

        super().save(*args, **kwargs)
        # Guarda normalmente el objeto en la base de datos