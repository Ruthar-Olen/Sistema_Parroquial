from django.contrib.auth.decorators import login_required, user_passes_test  # Seguridad de acceso
from django.shortcuts import render  # Permite renderizar templates HTML
from django.http import Http404  # Permite lanzar error 404 cuando un modelo no exista
from django.contrib import admin  # Permite leer el registro de modelos del admin original


def es_superusuario(user):
    # Verifica que el usuario exista, esté autenticado y además sea superusuario.
    return user.is_authenticated and user.is_superuser


@login_required  # Obliga a que el usuario haya iniciado sesión.
@user_passes_test(es_superusuario)  # Restringe el acceso únicamente a superusuarios.
def dashboard_administracion(request):
    # Construye el inventario de modelos usando exactamente los modelos registrados en /admin.
    modelos_admin = []

    # Recorre todos los modelos registrados en el panel admin original de Django.
    for modelo in admin.site._registry.keys():
        # Inicializa el total en cero por seguridad.
        total = 0

        # Intenta contar registros; si la tabla no existe en este entorno, deja 0 sin romper la vista.
        try:
            total = modelo.objects.count()
        except Exception:
            total = 0

        # Agrega la información del modelo a la lista que se mostrará en el dashboard.
        modelos_admin.append({
            'app_label': modelo._meta.app_label,
            'model_name': modelo._meta.model_name,
            'nombre_modelo': modelo._meta.verbose_name_plural.title(),
            'total': total,
        })

    # Ordena por app y nombre para mostrar una navegación clara y consistente.
    modelos_admin.sort(key=lambda x: (x['app_label'], x['nombre_modelo']))

    # Renderiza la vista principal del módulo de administración interna.
    return render(request, 'administracion/dashboard.html', {
        'modelos_admin': modelos_admin,
    })


@login_required  # Obliga a que el usuario haya iniciado sesión.
@user_passes_test(es_superusuario)  # Restringe el acceso únicamente a superusuarios.
def detalle_modelo(request, app_label, model_name):
    # Inicializa la variable donde se guardará el modelo encontrado.
    modelo_objetivo = None

    # Busca el modelo solicitado dentro del mismo registro del admin original.
    for modelo in admin.site._registry.keys():
        # Compara app_label y model_name para identificar el modelo correcto.
        if modelo._meta.app_label == app_label and modelo._meta.model_name == model_name:
            modelo_objetivo = modelo
            break

    # Si no se encuentra el modelo solicitado, devuelve error 404.
    if not modelo_objetivo:
        raise Http404('Modelo no encontrado en la configuración de administración.')

    # Obtiene todos los registros del modelo seleccionado.
    queryset = modelo_objetivo.objects.all()

    # Intenta ordenar descendente por clave primaria para mostrar primero los registros más recientes.
    try:
        queryset = queryset.order_by('-pk')
    except Exception:
        queryset = modelo_objetivo.objects.all()

    # Limita a 80 filas para mantener la pantalla ágil.
    registros = queryset[:80]

    # Renderiza la vista de detalle del modelo seleccionado.
    return render(request, 'administracion/detalle_modelo.html', {
        'app_label': app_label,
        'model_name': model_name,
        'nombre_modelo': modelo_objetivo._meta.verbose_name_plural.title(),
        'total': queryset.count(),
        'registros': registros,
    })