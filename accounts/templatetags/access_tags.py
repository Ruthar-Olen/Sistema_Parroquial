from django import template  # Importa herramientas para crear etiquetas de template

register = template.Library()  # Registra esta librería de etiquetas


@register.filter
def has_group(user, group_name):
    if not user.is_authenticated:
        return False  # Si no ha iniciado sesión, no pertenece a ningún grupo

    return user.groups.filter(name=group_name).exists()
    # Regresa True si el usuario pertenece al grupo indicado