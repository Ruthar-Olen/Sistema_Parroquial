from django.shortcuts import render, redirect, get_object_or_404  # Funciones base para renderizar, redirigir y buscar objetos
from django.contrib.auth.decorators import login_required, user_passes_test  # Decoradores para proteger vistas
from django.http import HttpResponse  # Respuesta HTTP para exportaciones
from .forms import InscripcionForm  # Formulario de inscripciones
from .models import Inscripcion  # Modelo principal
import csv  # Librería para exportar CSV
from openpyxl import Workbook  # Librería para exportar Excel


# ==============================
# 🔐 FUNCIONES DE PERMISOS
# ==============================

def es_direccion(user):
    return user.groups.filter(name='Direccion Parroquial').exists()  # Verifica si el usuario pertenece a Dirección

def es_secretaria(user):
    return user.groups.filter(name='Secretaria Parroquial').exists()  # Verifica si el usuario pertenece a Secretaría

def es_catequesis(user):
    return user.groups.filter(name='Coordinacion Catequesis').exists()  # Verifica si el usuario pertenece a Catequesis

def es_consulta(user):
    return user.groups.filter(name='Consulta').exists()  # Verifica si el usuario pertenece a Consulta


def puede_ver(user):
    return (
        user.is_superuser
        or es_direccion(user)
        or es_secretaria(user)
        or es_catequesis(user)
        or es_consulta(user)
    )  # Permiso para ver información

def puede_crear_editar(user):
    return (
        user.is_superuser
        or es_direccion(user)
        or es_secretaria(user)
    )  # Permiso para crear o editar

def puede_eliminar(user):
    return (
        user.is_superuser
        or es_direccion(user)
    )  # Permiso para eliminar


# ==============================
# 🔎 FILTRO REUTILIZABLE
# ==============================

def obtener_inscripciones_filtradas(request):
    query = request.GET.get('q', '')  # Obtiene texto de búsqueda
    tipo = request.GET.get('tipo', '')  # Obtiene filtro de tipo/sacramento

    inscripciones = Inscripcion.objects.all().order_by('-id')  # Lista base ordenada por ID descendente

    if query:
        inscripciones = inscripciones.filter(nombre_completo__icontains=query)  # Filtra por nombre

    if tipo:
        inscripciones = inscripciones.filter(tipo=tipo)  # Filtra por tipo

    return inscripciones, query, tipo  # Regresa queryset filtrado y filtros usados


# ==============================
# 📌 VISTAS
# ==============================

@login_required
@user_passes_test(puede_crear_editar)
def crear_inscripcion(request):
    if request.method == 'POST':
        form = InscripcionForm(request.POST)  # Crea formulario con datos enviados
        if form.is_valid():
            form.save()  # Guarda inscripción
            return redirect('lista_inscripciones')  # Regresa a la lista
    else:
        form = InscripcionForm()  # Formulario vacío

    return render(request, 'sacramentos/crear.html', {
        'form': form,
        'modo': 'crear'
    })  # Renderiza pantalla de creación


@login_required
@user_passes_test(puede_ver)
def lista_inscripciones(request):
    inscripciones, query, tipo = obtener_inscripciones_filtradas(request)  # Obtiene datos filtrados

    return render(request, 'sacramentos/lista.html', {
        'inscripciones': inscripciones,
        'query': query,
        'tipo': tipo,
        'puede_editar': puede_crear_editar(request.user),
        'puede_eliminar': puede_eliminar(request.user),
    })  # Renderiza lista operativa


@login_required
@user_passes_test(puede_ver)
def reporte_inscripciones(request):
    inscripciones, query, tipo = obtener_inscripciones_filtradas(request)  # Obtiene datos filtrados

    inscripciones = inscripciones.order_by(
        'grupo_catequesis__numero_grupo',  # Ordena primero por número de grupo
        'nombre_completo'  # Después por nombre
    )  # Este orden permite agrupar correctamente en el template

    return render(request, 'sacramentos/reporte.html', {
        'inscripciones': inscripciones,
        'query': query,
        'tipo': tipo,
    })  # Renderiza reporte agrupado


@login_required
@user_passes_test(puede_crear_editar)
def editar_inscripcion(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)  # Busca inscripción existente

    if request.method == 'POST':
        form = InscripcionForm(request.POST, instance=inscripcion)  # Formulario con instancia
        if form.is_valid():
            form.save()  # Guarda cambios
            return redirect('lista_inscripciones')  # Regresa a la lista
    else:
        form = InscripcionForm(instance=inscripcion)  # Carga datos actuales

    return render(request, 'sacramentos/crear.html', {
        'form': form,
        'modo': 'editar',
        'inscripcion': inscripcion
    })  # Renderiza pantalla de edición


@login_required
@user_passes_test(puede_eliminar)
def eliminar_inscripcion(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)  # Busca inscripción a eliminar

    if request.method == 'POST':
        inscripcion.delete()  # Elimina registro
        return redirect('lista_inscripciones')  # Regresa a lista

    return render(request, 'sacramentos/eliminar.html', {
        'inscripcion': inscripcion
    })  # Pide confirmación


@login_required
@user_passes_test(puede_ver)
def detalle_inscripcion(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)  # Busca expediente por ID

    return render(request, 'sacramentos/detalle.html', {
        'inscripcion': inscripcion,
        'puede_editar': puede_crear_editar(request.user),
    })  # Renderiza expediente individual


# ==============================
# 📤 EXPORTAR CSV
# ==============================

@login_required
@user_passes_test(puede_ver)
def exportar_inscripciones_csv(request):
    inscripciones, query, tipo = obtener_inscripciones_filtradas(request)  # Obtiene datos filtrados

    response = HttpResponse(content_type='text/csv; charset=utf-8')  # Respuesta tipo CSV
    response['Content-Disposition'] = 'attachment; filename="inscripciones.csv"'  # Nombre del archivo

    response.write('\ufeff')  # BOM para que Excel respete acentos
    writer = csv.writer(response)  # Escritor CSV

    writer.writerow([
        'ID',
        'Tipo',
        'Fecha',
        'Nombre completo',
        'Telefono',
        'Edad',
        'Nombre padre',
        'Nombre madre',
        'Nombre padrino',
        'Nombre madrina',
        'Catequista',
        'Grupo',
        'Lugar clases',
        'Dia clases',
        'Hora clases',
        'Bautizo',
        'Eucaristia',
        'Confirmacion',
        'Matrimonio',
        'Acta nacimiento',
        'Boleta bautizo',
        'Boleta confirmacion',
        'INE',
        'Otros documentos',
    ])  # Encabezados

    for ins in inscripciones:
        writer.writerow([
            ins.id,
            ins.get_tipo_display(),
            ins.fecha.strftime('%d/%m/%Y') if ins.fecha else '',
            ins.nombre_completo,
            ins.telefono,
            ins.edad,
            ins.nombre_padre,
            ins.nombre_madre,
            ins.nombre_padrino,
            ins.nombre_madrina,
            str(ins.catequista) if ins.catequista else '',
            str(ins.grupo_catequesis) if ins.grupo_catequesis else '',
            ins.lugar_clases,
            ins.dia_clases,
            ins.hora_clases,
            'Sí' if ins.bautizo else 'No',
            'Sí' if ins.eucaristia else 'No',
            'Sí' if ins.confirmacion else 'No',
            'Sí' if ins.matrimonio else 'No',
            'Sí' if ins.acta_nacimiento else 'No',
            'Sí' if ins.boleta_bautizo else 'No',
            'Sí' if ins.boleta_confirmacion else 'No',
            'Sí' if ins.ine else 'No',
            ins.otros_documentos,
        ])  # Datos por fila

    return response  # Devuelve archivo


# ==============================
# 📤 EXPORTAR EXCEL
# ==============================

@login_required
@user_passes_test(puede_ver)
def exportar_inscripciones_excel(request):
    inscripciones, query, tipo = obtener_inscripciones_filtradas(request)  # Obtiene datos filtrados

    wb = Workbook()  # Crea libro Excel
    ws = wb.active  # Selecciona hoja activa
    ws.title = 'Inscripciones'  # Nombre de la hoja

    encabezados = [
        'ID',
        'Tipo',
        'Fecha',
        'Nombre completo',
        'Telefono',
        'Edad',
        'Nombre padre',
        'Nombre madre',
        'Nombre padrino',
        'Nombre madrina',
        'Catequista',
        'Grupo',
        'Lugar clases',
        'Dia clases',
        'Hora clases',
        'Bautizo',
        'Eucaristia',
        'Confirmacion',
        'Matrimonio',
        'Acta nacimiento',
        'Boleta bautizo',
        'Boleta confirmacion',
        'INE',
        'Otros documentos',
    ]  # Encabezados de Excel

    ws.append(encabezados)  # Inserta encabezados

    for ins in inscripciones:
        ws.append([
            ins.id,
            ins.get_tipo_display(),
            ins.fecha.strftime('%d/%m/%Y') if ins.fecha else '',
            ins.nombre_completo,
            ins.telefono,
            ins.edad,
            ins.nombre_padre,
            ins.nombre_madre,
            ins.nombre_padrino,
            ins.nombre_madrina,
            str(ins.catequista) if ins.catequista else '',
            str(ins.grupo_catequesis) if ins.grupo_catequesis else '',
            ins.lugar_clases,
            ins.dia_clases,
            ins.hora_clases,
            'Sí' if ins.bautizo else 'No',
            'Sí' if ins.eucaristia else 'No',
            'Sí' if ins.confirmacion else 'No',
            'Sí' if ins.matrimonio else 'No',
            'Sí' if ins.acta_nacimiento else 'No',
            'Sí' if ins.boleta_bautizo else 'No',
            'Sí' if ins.boleta_confirmacion else 'No',
            'Sí' if ins.ine else 'No',
            ins.otros_documentos,
        ])  # Inserta cada inscripción

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )  # Tipo de respuesta Excel
    response['Content-Disposition'] = 'attachment; filename="inscripciones.xlsx"'  # Nombre del archivo

    wb.save(response)  # Guarda libro en la respuesta
    return response  # Devuelve archivo