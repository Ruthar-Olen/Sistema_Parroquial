from django.shortcuts import render, redirect, get_object_or_404  # Funciones base para vistas
from django.contrib.auth.decorators import login_required, user_passes_test  # Decoradores de permisos
from django.views.decorators.cache import never_cache  # Evita cache en vistas sensibles
from django.http import JsonResponse  # Permite responder JSON para peticiones dinámicas
from django.templatetags.static import static  # Permite construir rutas de archivos estáticos

from .models import (
    Catequista,
    GrupoCatequesis,
    HorarioCatequesis,
    FormatoCatequesis,
)  # Importa los modelos del módulo catequesis

from .forms import (
    CatequistaForm,
    GrupoCatequesisForm,
    HorarioCatequesisForm,
    FormatoCatequesisForm,
)  # Importa formularios del módulo


def es_catequesis(user):
    return user.is_superuser or user.groups.filter(name='Coordinacion Catequesis').exists()
    # Permite acceso solo a superusuario o al grupo de Coordinación Catequesis


@never_cache
@login_required
@user_passes_test(es_catequesis)
def menu_catequesis(request):
    catequistas = Catequista.objects.all().order_by('nombre')
    # Obtiene todos los catequistas ordenados alfabéticamente

    grupos = GrupoCatequesis.objects.select_related('catequista').all().order_by('numero_grupo')
    # Obtiene los grupos junto con su catequista y los ordena por número de grupo

    horarios = HorarioCatequesis.objects.select_related('grupo').all().order_by('grupo__numero_grupo', 'hora_inicio')
    # Obtiene los horarios junto con su grupo y los ordena por grupo y hora de inicio

    return render(request, 'catequesis/menu.html', {
        'catequistas': catequistas,
        'grupos': grupos,
        'horarios': horarios,
    })
    # Renderiza el menú principal de catequesis


# =========================
# CATEQUISTAS
# =========================

@never_cache
@login_required
@user_passes_test(es_catequesis)
def lista_catequistas(request):
    catequistas = Catequista.objects.all().order_by('nombre')
    # Obtiene todos los catequistas ordenados por nombre

    return render(request, 'catequesis/catequistas/lista.html', {
        'catequistas': catequistas
    })
    # Renderiza la lista de catequistas


@never_cache
@login_required
@user_passes_test(es_catequesis)
def crear_catequista(request):
    if request.method == 'POST':
        form = CatequistaForm(request.POST)
        # Carga el formulario con los datos enviados

        if form.is_valid():
            form.save()
            # Guarda el catequista si el formulario es válido

            return redirect('lista_catequistas')
            # Regresa a la lista de catequistas
    else:
        form = CatequistaForm()
        # Si no es POST, muestra el formulario vacío

    return render(request, 'catequesis/catequistas/form.html', {
        'form': form,
        'modo': 'crear'
    })
    # Renderiza el formulario de creación


@never_cache
@login_required
@user_passes_test(es_catequesis)
def editar_catequista(request, pk):
    catequista = get_object_or_404(Catequista, pk=pk)
    # Busca el catequista por su ID o devuelve 404

    if request.method == 'POST':
        form = CatequistaForm(request.POST, instance=catequista)
        # Carga el formulario con datos enviados sobre la instancia actual

        if form.is_valid():
            form.save()
            # Guarda los cambios si el formulario es válido

            return redirect('lista_catequistas')
            # Regresa a la lista de catequistas
    else:
        form = CatequistaForm(instance=catequista)
        # Si no es POST, muestra el formulario con los datos actuales

    return render(request, 'catequesis/catequistas/form.html', {
        'form': form,
        'modo': 'editar',
        'objeto': catequista
    })
    # Renderiza el formulario de edición


@never_cache
@login_required
@user_passes_test(es_catequesis)
def eliminar_catequista(request, pk):
    catequista = get_object_or_404(Catequista, pk=pk)
    # Busca el catequista por su ID o devuelve 404

    if request.method == 'POST':
        catequista.delete()
        # Elimina el catequista confirmado

        return redirect('lista_catequistas')
        # Regresa a la lista de catequistas

    return render(request, 'catequesis/catequistas/eliminar.html', {
        'objeto': catequista
    })
    # Renderiza la pantalla de confirmación de eliminación


# =========================
# GRUPOS
# =========================

@never_cache
@login_required
@user_passes_test(es_catequesis)
def lista_grupos(request):
    grupos = GrupoCatequesis.objects.select_related('catequista').all().order_by('numero_grupo')
    # Obtiene los grupos junto con su catequista y los ordena por número de grupo

    return render(request, 'catequesis/grupos/lista.html', {
        'grupos': grupos
    })
    # Renderiza la lista de grupos


@never_cache
@login_required
@user_passes_test(es_catequesis)
def crear_grupo(request):
    if request.method == 'POST':
        form = GrupoCatequesisForm(request.POST)
        # Carga el formulario con los datos enviados

        if form.is_valid():
            form.save()
            # Guarda el grupo si el formulario es válido

            return redirect('lista_grupos')
            # Regresa a la lista de grupos
    else:
        form = GrupoCatequesisForm()
        # Si no es POST, muestra el formulario vacío

    return render(request, 'catequesis/grupos/form.html', {
        'form': form,
        'modo': 'crear'
    })
    # Renderiza el formulario de creación de grupo


@never_cache
@login_required
@user_passes_test(es_catequesis)
def editar_grupo(request, pk):
    grupo = get_object_or_404(GrupoCatequesis, pk=pk)
    # Busca el grupo por su ID o devuelve 404

    if request.method == 'POST':
        form = GrupoCatequesisForm(request.POST, instance=grupo)
        # Carga el formulario con datos enviados sobre la instancia actual

        if form.is_valid():
            form.save()
            # Guarda los cambios si el formulario es válido

            return redirect('lista_grupos')
            # Regresa a la lista de grupos
    else:
        form = GrupoCatequesisForm(instance=grupo)
        # Si no es POST, muestra el formulario con los datos actuales

    return render(request, 'catequesis/grupos/form.html', {
        'form': form,
        'modo': 'editar',
        'objeto': grupo
    })
    # Renderiza el formulario de edición de grupo


@never_cache
@login_required
@user_passes_test(es_catequesis)
def eliminar_grupo(request, pk):
    grupo = get_object_or_404(GrupoCatequesis, pk=pk)
    # Busca el grupo por su ID o devuelve 404

    if request.method == 'POST':
        grupo.delete()
        # Elimina el grupo confirmado

        return redirect('lista_grupos')
        # Regresa a la lista de grupos

    return render(request, 'catequesis/grupos/eliminar.html', {
        'objeto': grupo
    })
    # Renderiza la pantalla de confirmación de eliminación


# =========================
# HORARIOS
# =========================

@never_cache
@login_required
@user_passes_test(es_catequesis)
def lista_horarios(request):
    horarios = HorarioCatequesis.objects.select_related('grupo').all().order_by('grupo__numero_grupo', 'hora_inicio')
    # Obtiene los horarios junto con su grupo y los ordena por grupo y hora

    return render(request, 'catequesis/horarios/lista.html', {
        'horarios': horarios
    })
    # Renderiza la lista de horarios


@never_cache
@login_required
@user_passes_test(es_catequesis)
def crear_horario(request):
    if request.method == 'POST':
        form = HorarioCatequesisForm(request.POST)
        # Carga el formulario con los datos enviados

        if form.is_valid():
            form.save()
            # Guarda el horario si el formulario es válido

            return redirect('lista_horarios')
            # Regresa a la lista de horarios
    else:
        form = HorarioCatequesisForm()
        # Si no es POST, muestra el formulario vacío

    return render(request, 'catequesis/horarios/form.html', {
        'form': form,
        'modo': 'crear'
    })
    # Renderiza el formulario de creación de horario


@never_cache
@login_required
@user_passes_test(es_catequesis)
def editar_horario(request, pk):
    horario = get_object_or_404(HorarioCatequesis, pk=pk)
    # Busca el horario por su ID o devuelve 404

    if request.method == 'POST':
        form = HorarioCatequesisForm(request.POST, instance=horario)
        # Carga el formulario con datos enviados sobre la instancia actual

        if form.is_valid():
            form.save()
            # Guarda los cambios si el formulario es válido

            return redirect('lista_horarios')
            # Regresa a la lista de horarios
    else:
        form = HorarioCatequesisForm(instance=horario)
        # Si no es POST, muestra el formulario con los datos actuales

    return render(request, 'catequesis/horarios/form.html', {
        'form': form,
        'modo': 'editar',
        'objeto': horario
    })
    # Renderiza el formulario de edición de horario


@never_cache
@login_required
@user_passes_test(es_catequesis)
def eliminar_horario(request, pk):
    horario = get_object_or_404(HorarioCatequesis, pk=pk)
    # Busca el horario por su ID o devuelve 404

    if request.method == 'POST':
        horario.delete()
        # Elimina el horario confirmado

        return redirect('lista_horarios')
        # Regresa a la lista de horarios

    return render(request, 'catequesis/horarios/eliminar.html', {
        'objeto': horario
    })
    # Renderiza la pantalla de confirmación de eliminación


# =========================
# FORMATOS
# =========================

@never_cache
@login_required
@user_passes_test(es_catequesis)
def lista_formatos(request):
    formatos = FormatoCatequesis.objects.select_related('tipo').all().order_by('tipo__nombre', '-activo')
    # Obtiene todos los formatos y trae el tipo relacionado en la misma consulta

    return render(request, 'catequesis/formatos/lista.html', {
        'formatos': formatos
    })
    # Renderiza la lista de formatos fuera del admin


@never_cache
@login_required
@user_passes_test(es_catequesis)
def editar_formato(request, pk):
    formato = get_object_or_404(FormatoCatequesis, pk=pk)
    # Busca el formato por su ID o devuelve 404

    if request.method == 'POST':
        form = FormatoCatequesisForm(request.POST, instance=formato)
        # Carga el formulario con datos enviados sobre la instancia actual

        if form.is_valid():
            form.save()
            # Guarda los cambios del formato

            return redirect('lista_formatos')
            # Regresa a la lista de formatos
    else:
        form = FormatoCatequesisForm(instance=formato)
        # Si no es POST, muestra el formulario con los datos actuales

    return render(request, 'catequesis/formatos/form.html', {
        'form': form,
        'modo': 'editar',
        'objeto': formato
    })
    # Renderiza el formulario de edición del formato


@never_cache
@login_required
@user_passes_test(es_catequesis)
def preview_formato(request, pk):
    formato = get_object_or_404(FormatoCatequesis.objects.select_related('tipo'), pk=pk)
    # Busca el formato por su ID y trae el tipo relacionado en la misma consulta

    celdas = formato.celdas.all().order_by('fila', 'columna')
    # Obtiene las celdas del formato ordenadas por fila y columna

    max_fila = 0
    # Inicializa el número máximo de fila

    max_columna = 0
    # Inicializa el número máximo de columna

    for celda in celdas:
        if celda.fila > max_fila:
            max_fila = celda.fila
            # Guarda la fila mayor encontrada

        if celda.columna > max_columna:
            max_columna = celda.columna
            # Guarda la columna mayor encontrada

    matriz_celdas = []
    # Aquí se construirá la cuadrícula final para el preview

    if formato.usa_celdas and max_fila > 0 and max_columna > 0:
        mapa_celdas = {
            (celda.fila, celda.columna): celda.contenido
            for celda in celdas
        }
        # Convierte las celdas en un diccionario para ubicarlas por fila y columna

        for fila in range(1, max_fila + 1):
            fila_actual = []
            # Crea una fila temporal vacía

            for columna in range(1, max_columna + 1):
                fila_actual.append(mapa_celdas.get((fila, columna), ''))
                # Inserta el contenido correspondiente o un texto vacío si no existe

            matriz_celdas.append(fila_actual)
            # Agrega la fila completa a la matriz final

    nombre_impresion = 'NOMBRE DE PRUEBA'
    # Define un nombre de ejemplo para la vista previa

    grupo_impresion = '1A'
    # Define un grupo de ejemplo para la vista previa

    template_preview = 'sacramentos/formatos/nino.html'
    # Usa por defecto el template del formato de niño

    if formato.tipo.clave.upper() == 'PAPAS':
        template_preview = 'sacramentos/formatos/papas.html'
        # Si el tipo es Papás usa el template correspondiente

        nombre_impresion = 'PADRE DE PRUEBA Y MADRE DE PRUEBA'
        # Cambia el nombre de prueba para el formato de papás

    elif formato.tipo.clave.upper() == 'TARJETON':
        template_preview = 'sacramentos/formatos/tarjeton.html'
        # Si el tipo es Tarjetón usa el template correspondiente

    url_logo_fondo = static('img/logo_parroquia.jpg')
    # Construye la ruta del logo o imagen de fondo para la vista previa HTML

    return render(request, template_preview, {
        'formato': formato,
        'nombre_impresion': nombre_impresion,
        'grupo_impresion': grupo_impresion,
        'matriz_celdas': matriz_celdas,
        'url_logo_fondo': url_logo_fondo,
    })
    # Renderiza la vista previa del formato directamente en navegador


# =========================
# API PARA INSCRIPCIONES
# =========================

@never_cache
@login_required
def grupos_por_catequista(request):
    catequista_id = request.GET.get('catequista_id')
    # Obtiene el ID del catequista enviado por GET

    grupos = []
    # Inicializa la respuesta vacía

    if catequista_id:
        grupos_qs = GrupoCatequesis.objects.filter(
            catequista_id=catequista_id
        ).order_by('numero_grupo')
        # Filtra los grupos pertenecientes al catequista seleccionado

        grupos = [
            {
                'id': grupo.id,
                'nombre': grupo.numero_grupo
            }
            for grupo in grupos_qs
        ]
        # Convierte los grupos a una lista simple en formato JSON

    return JsonResponse({'grupos': grupos})
    # Devuelve la lista de grupos en JSON


@never_cache
@login_required
def horarios_por_grupo(request):
    grupo_id = request.GET.get('grupo_id')
    # Obtiene el ID del grupo enviado por GET

    horarios = []
    # Inicializa la respuesta vacía

    if grupo_id:
        horarios_qs = HorarioCatequesis.objects.filter(
            grupo_id=grupo_id
        ).select_related('grupo').order_by('hora_inicio')
        # Filtra los horarios del grupo y trae su grupo relacionado

        horarios = [
            {
                'id': horario.id,
                'nombre': f"{horario.hora_inicio.strftime('%H:%M')} a {horario.hora_fin.strftime('%H:%M')}",
                'hora_inicio': horario.hora_inicio.strftime('%H:%M'),
                'hora_fin': horario.hora_fin.strftime('%H:%M'),
                'grupo': horario.grupo.numero_grupo,
                'lugar': horario.grupo.lugar,
                'dia': horario.grupo.dia,
            }
            for horario in horarios_qs
        ]
        # Convierte los horarios a una lista simple en formato JSON

    return JsonResponse({'horarios': horarios})
    # Devuelve la lista de horarios en JSON