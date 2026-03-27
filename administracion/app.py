from django.apps import AppConfig  # Permite configurar metadatos de la app


class AdministracionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # Tipo de llave primaria por defecto
    name = 'administracion'  # Nombre técnico de la app
    verbose_name = 'Administración interna'  # Nombre legible en ecosistema Django