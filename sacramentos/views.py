from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse
from .forms import InscripcionForm
from .models import Inscripcion
import csv
from openpyxl import Workbook


# ==============================
# 🔐 FUNCIONES DE PERMISOS
# ==============================

def es_direccion(user):
    return user.groups.filter(name='Direccion Parroquial').exists()

def es_secretaria(user):
    return user.groups.filter(name='Secretaria Parroquial').exists()

def es_catequesis(user):
    return user.groups.filter(name='Coordinacion Catequesis').exists()

def es_consulta(user):
    return user.groups.filter(name='Consulta').exists()


def puede_ver(user):
    return (
        user.is_superuser
        or es_direccion(user)
        or es_secretaria(user)
        or es_catequesis(user)
        or es_consulta(user)
    )

def puede_crear_editar(user):
    return (
        user.is_superuser
        or es_direccion(user)
        or es_secretaria(user)
    )

def puede_eliminar(user):
    return (
        user.is_superuser
        or es_direccion(user)
    )


# ==============================
# 🔎 FILTRO REUTILIZABLE
# ==============================

def obtener_inscripciones_filtradas(request):
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')

    inscripciones = Inscripcion.objects.all().order_by('-id')

    if query:
        inscripciones = inscripciones.filter(nombre_completo__icontains=query)

    if tipo:
        inscripciones = inscripciones.filter(tipo=tipo)

    return inscripciones, query, tipo


# ==============================
# 📌 VISTAS
# ==============================

@login_required
@user_passes_test(puede_crear_editar)
def crear_inscripcion(request):
    if request.method == 'POST':
        form = InscripcionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_inscripciones')
    else:
        form = InscripcionForm()

    return render(request, 'sacramentos/crear.html', {
        'form': form,
        'modo': 'crear'
    })


@login_required
@user_passes_test(puede_ver)
def lista_inscripciones(request):
    inscripciones, query, tipo = obtener_inscripciones_filtradas(request)

    return render(request, 'sacramentos/lista.html', {
        'inscripciones': inscripciones,
        'query': query,
        'tipo': tipo,
        'puede_editar': puede_crear_editar(request.user),
        'puede_eliminar': puede_eliminar(request.user),
    })


@login_required
@user_passes_test(puede_ver)
def reporte_inscripciones(request):
    inscripciones, query, tipo = obtener_inscripciones_filtradas(request)

    return render(request, 'sacramentos/reporte.html', {
        'inscripciones': inscripciones,
        'query': query,
        'tipo': tipo,
    })


@login_required
@user_passes_test(puede_crear_editar)
def editar_inscripcion(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)

    if request.method == 'POST':
        form = InscripcionForm(request.POST, instance=inscripcion)
        if form.is_valid():
            form.save()
            return redirect('lista_inscripciones')
    else:
        form = InscripcionForm(instance=inscripcion)

    return render(request, 'sacramentos/crear.html', {
        'form': form,
        'modo': 'editar',
        'inscripcion': inscripcion
    })


@login_required
@user_passes_test(puede_eliminar)
def eliminar_inscripcion(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)

    if request.method == 'POST':
        inscripcion.delete()
        return redirect('lista_inscripciones')

    return render(request, 'sacramentos/eliminar.html', {
        'inscripcion': inscripcion
    })


@login_required
@user_passes_test(puede_ver)
def detalle_inscripcion(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)

    return render(request, 'sacramentos/detalle.html', {
        'inscripcion': inscripcion,
        'puede_editar': puede_crear_editar(request.user),
    })


# ==============================
# 📤 EXPORTAR CSV
# ==============================

@login_required
@user_passes_test(puede_ver)
def exportar_inscripciones_csv(request):
    inscripciones, query, tipo = obtener_inscripciones_filtradas(request)

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="inscripciones.csv"'

    response.write('\ufeff')
    writer = csv.writer(response)

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
    ])

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
        ])

    return response


# ==============================
# 📤 EXPORTAR EXCEL
# ==============================

@login_required
@user_passes_test(puede_ver)
def exportar_inscripciones_excel(request):
    inscripciones, query, tipo = obtener_inscripciones_filtradas(request)

    wb = Workbook()
    ws = wb.active
    ws.title = 'Inscripciones'

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
    ]

    ws.append(encabezados)

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
        ])

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="inscripciones.xlsx"'

    wb.save(response)
    return response