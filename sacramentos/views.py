from django.shortcuts import render, redirect, get_object_or_404  # Funciones base para vistas
from django.contrib.auth.decorators import login_required, user_passes_test  # Decoradores de permisos
from django.http import HttpResponse  # Respuesta HTTP para exportaciones
from django.conf import settings  # Acceso a la configuración del proyecto
from .forms import InscripcionForm  # Formulario de inscripciones
from .models import Inscripcion  # Modelo principal
import csv  # Librería para CSV
import os  # Librería para manejar rutas
from collections import OrderedDict  # Estructura ordenada para agrupar por grupo
from openpyxl import Workbook  # Librería para Excel

from reportlab.lib import colors  # Colores para PDF
from reportlab.lib.pagesizes import letter, landscape  # Tamaños de página
from reportlab.lib.units import mm  # Unidad milímetros
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # Estilos de texto
from reportlab.platypus import (  # Componentes para construir PDFs
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)


# ==============================
# 🔐 FUNCIONES DE PERMISOS
# ==============================

def es_direccion(user):
    return user.groups.filter(name='Direccion Parroquial').exists()  # Revisa si el usuario pertenece a Dirección

def es_secretaria(user):
    return user.groups.filter(name='Secretaria Parroquial').exists()  # Revisa si el usuario pertenece a Secretaría

def es_catequesis(user):
    return user.groups.filter(name='Coordinacion Catequesis').exists()  # Revisa si el usuario pertenece a Catequesis

def es_consulta(user):
    return user.groups.filter(name='Consulta').exists()  # Revisa si el usuario pertenece a Consulta


def puede_ver(user):
    return (
        user.is_superuser
        or es_direccion(user)
        or es_secretaria(user)
        or es_catequesis(user)
        or es_consulta(user)
    )  # Permiso para visualizar

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
    query = request.GET.get('q', '')  # Obtiene el filtro por nombre
    tipo = request.GET.get('tipo', '')  # Obtiene el filtro por tipo de sacramento

    inscripciones = Inscripcion.objects.all().order_by('-id')  # Consulta base ordenada por ID descendente

    if query:
        inscripciones = inscripciones.filter(nombre_completo__icontains=query)  # Filtra por nombre

    if tipo:
        inscripciones = inscripciones.filter(tipo=tipo)  # Filtra por tipo

    return inscripciones, query, tipo  # Devuelve resultados y filtros


# ==============================
# 📚 AGRUPACIÓN POR GRUPO
# ==============================

def agrupar_inscripciones_por_grupo(inscripciones):
    grupos = OrderedDict()  # Crea contenedor ordenado para agrupar registros

    for ins in inscripciones:  # Recorre cada inscripción
        if ins.grupo_catequesis:
            nombre_grupo = str(ins.grupo_catequesis)  # Toma el nombre del grupo
        else:
            nombre_grupo = 'Sin grupo asignado'  # Nombre alterno si no hay grupo

        if nombre_grupo not in grupos:
            grupos[nombre_grupo] = []  # Crea la lista del grupo si no existe

        grupos[nombre_grupo].append(ins)  # Agrega la inscripción al grupo correspondiente

    return grupos  # Devuelve grupos ya organizados


# ==============================
# 📌 VISTAS PRINCIPALES
# ==============================

@login_required
@user_passes_test(puede_crear_editar)
def crear_inscripcion(request):
    if request.method == 'POST':
        form = InscripcionForm(request.POST)  # Carga el formulario con datos del POST
        if form.is_valid():
            form.save()  # Guarda inscripción
            return redirect('lista_inscripciones')  # Redirige a la lista
    else:
        form = InscripcionForm()  # Crea formulario vacío

    return render(request, 'sacramentos/crear.html', {
        'form': form,
        'modo': 'crear'
    })  # Renderiza la vista de creación


@login_required
@user_passes_test(puede_ver)
def lista_inscripciones(request):
    inscripciones, query, tipo = obtener_inscripciones_filtradas(request)  # Obtiene inscripciones filtradas

    return render(request, 'sacramentos/lista.html', {
        'inscripciones': inscripciones,
        'query': query,
        'tipo': tipo,
        'puede_editar': puede_crear_editar(request.user),
        'puede_eliminar': puede_eliminar(request.user),
    })  # Renderiza la lista resumida


@login_required
@user_passes_test(puede_ver)
def reporte_inscripciones(request):
    inscripciones, query, tipo = obtener_inscripciones_filtradas(request)  # Obtiene resultados filtrados

    inscripciones = inscripciones.order_by(
        'grupo_catequesis__numero_grupo',  # Ordena por grupo
        'nombre_completo'  # Después por nombre
    )

    return render(request, 'sacramentos/reporte.html', {
        'inscripciones': inscripciones,
        'query': query,
        'tipo': tipo,
    })  # Renderiza reporte agrupado en pantalla


@login_required
@user_passes_test(puede_crear_editar)
def editar_inscripcion(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)  # Busca la inscripción a editar

    if request.method == 'POST':
        form = InscripcionForm(request.POST, instance=inscripcion)  # Carga formulario con instancia actual
        if form.is_valid():
            form.save()  # Guarda cambios
            return redirect('lista_inscripciones')  # Regresa a lista
    else:
        form = InscripcionForm(instance=inscripcion)  # Muestra datos actuales

    return render(request, 'sacramentos/crear.html', {
        'form': form,
        'modo': 'editar',
        'inscripcion': inscripcion
    })  # Renderiza formulario de edición


@login_required
@user_passes_test(puede_eliminar)
def eliminar_inscripcion(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)  # Busca la inscripción

    if request.method == 'POST':
        inscripcion.delete()  # Elimina el registro
        return redirect('lista_inscripciones')  # Regresa a lista

    return render(request, 'sacramentos/eliminar.html', {
        'inscripcion': inscripcion
    })  # Renderiza pantalla de confirmación


@login_required
@user_passes_test(puede_ver)
def detalle_inscripcion(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)  # Busca inscripción individual

    return render(request, 'sacramentos/detalle.html', {
        'inscripcion': inscripcion,
        'puede_editar': puede_crear_editar(request.user),
    })  # Renderiza expediente en pantalla


# ==============================
# 📤 EXPORTAR CSV
# ==============================

@login_required
@user_passes_test(puede_ver)
def exportar_inscripciones_csv(request):
    inscripciones, query, tipo = obtener_inscripciones_filtradas(request)  # Obtiene lista filtrada

    response = HttpResponse(content_type='text/csv; charset=utf-8')  # Define tipo de archivo
    response['Content-Disposition'] = 'attachment; filename="inscripciones.csv"'  # Nombre del archivo

    response.write('\ufeff')  # Agrega BOM para que Excel respete acentos
    writer = csv.writer(response)  # Crea escritor CSV

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
    ])  # Encabezados del CSV

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
        ])  # Fila por inscripción

    return response  # Devuelve CSV


# ==============================
# 📤 EXPORTAR EXCEL
# ==============================

@login_required
@user_passes_test(puede_ver)
def exportar_inscripciones_excel(request):
    inscripciones, query, tipo = obtener_inscripciones_filtradas(request)  # Obtiene lista filtrada

    wb = Workbook()  # Crea libro de Excel
    ws = wb.active  # Selecciona hoja activa
    ws.title = 'Inscripciones'  # Nombra la hoja

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
        ])  # Agrega cada fila

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )  # Define tipo Excel
    response['Content-Disposition'] = 'attachment; filename="inscripciones.xlsx"'  # Nombre del archivo

    wb.save(response)  # Guarda el libro en la respuesta
    return response  # Devuelve Excel


# ==============================
# 📤 PDF BONITO DE EXPEDIENTE
# ==============================

@login_required
@user_passes_test(puede_ver)
def exportar_expediente_pdf(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)  # Busca la inscripción

    response = HttpResponse(content_type='application/pdf')  # Define tipo PDF
    response['Content-Disposition'] = f'attachment; filename="expediente_{inscripcion.id}.pdf"'  # Nombre del archivo

    doc = SimpleDocTemplate(
        response,  # La salida será la respuesta
        pagesize=letter,  # Tamaño carta vertical
        rightMargin=14 * mm,  # Margen derecho
        leftMargin=14 * mm,  # Margen izquierdo
        topMargin=12 * mm,  # Margen superior
        bottomMargin=12 * mm,  # Margen inferior
    )

    elementos = []  # Lista de elementos del PDF
    styles = getSampleStyleSheet()  # Estilos base

    estilo_titulo = ParagraphStyle(
        'TituloParroquia',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#1f3557'),
        spaceAfter=6,
        alignment=1,
    )  # Estilo del título principal

    estilo_subtitulo = ParagraphStyle(
        'SubtituloParroquia',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#555555'),
        spaceAfter=10,
        alignment=1,
    )  # Estilo del subtítulo

    estilo_seccion = ParagraphStyle(
        'SeccionParroquia',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor('#1f3557'),
        spaceBefore=8,
        spaceAfter=6,
    )  # Estilo para encabezados de sección

    ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo_parroquia.jpg')  # Ruta física del logo

    if os.path.exists(ruta_logo):
        logo = Image(ruta_logo, width=28 * mm, height=28 * mm)  # Carga logo
        logo.hAlign = 'CENTER'  # Centra logo
        elementos.append(logo)  # Agrega logo
        elementos.append(Spacer(1, 4))  # Espacio debajo

    elementos.append(Paragraph('Parroquia Santísima Trinidad', estilo_titulo))  # Nombre de la parroquia
    elementos.append(Paragraph('Expediente de inscripción sacramental', estilo_subtitulo))  # Subtítulo
    elementos.append(Spacer(1, 4))  # Espacio inferior

    elementos.append(Paragraph('Datos generales', estilo_seccion))  # Sección datos generales

    tabla_generales = Table([
        ['ID', str(inscripcion.id), 'Fecha', inscripcion.fecha.strftime('%d/%m/%Y') if inscripcion.fecha else '-'],
        ['Nombre completo', inscripcion.nombre_completo or '-', 'Sacramento', inscripcion.get_tipo_display()],
        ['Teléfono', inscripcion.telefono or '-', 'Edad', str(inscripcion.edad or '-')],
    ], colWidths=[35 * mm, 55 * mm, 35 * mm, 50 * mm])  # Tabla de datos generales

    tabla_generales.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fbfcfe')),
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#cfd8e3')),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#dfe6ef')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))  # Estilos de tabla

    elementos.append(tabla_generales)  # Agrega tabla generales

    elementos.append(Paragraph('Familia y vínculos', estilo_seccion))  # Sección familia

    tabla_familia = Table([
        ['Padre', inscripcion.nombre_padre or '-', 'Madre', inscripcion.nombre_madre or '-'],
        ['Padrino', inscripcion.nombre_padrino or '-', 'Madrina', inscripcion.nombre_madrina or '-'],
    ], colWidths=[35 * mm, 55 * mm, 35 * mm, 50 * mm])  # Tabla familia

    tabla_familia.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#cfd8e3')),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#dfe6ef')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))  # Estilos tabla familia

    elementos.append(tabla_familia)  # Agrega familia

    elementos.append(Paragraph('Catequesis', estilo_seccion))  # Sección catequesis

    tabla_catequesis = Table([
        ['Catequista', str(inscripcion.catequista) if inscripcion.catequista else '-', 'Grupo', str(inscripcion.grupo_catequesis) if inscripcion.grupo_catequesis else '-'],
        ['Lugar', inscripcion.lugar_clases or '-', 'Día', inscripcion.dia_clases or '-'],
        ['Hora', inscripcion.hora_clases or '-', '', ''],
    ], colWidths=[35 * mm, 55 * mm, 35 * mm, 50 * mm])  # Tabla catequesis

    tabla_catequesis.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fbfcfe')),
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#cfd8e3')),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#dfe6ef')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))  # Estilos tabla catequesis

    elementos.append(tabla_catequesis)  # Agrega catequesis

    elementos.append(Paragraph('Historial sacramental', estilo_seccion))  # Sección historial

    tabla_historial = Table([
        ['Bautizo', 'Sí' if inscripcion.bautizo else 'No', 'Eucaristía', 'Sí' if inscripcion.eucaristia else 'No'],
        ['Confirmación', 'Sí' if inscripcion.confirmacion else 'No', 'Matrimonio', 'Sí' if inscripcion.matrimonio else 'No'],
    ], colWidths=[35 * mm, 20 * mm, 35 * mm, 20 * mm])  # Tabla historial

    tabla_historial.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#cfd8e3')),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#dfe6ef')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))  # Estilos historial

    elementos.append(tabla_historial)  # Agrega historial

    elementos.append(Paragraph('Documentos entregados', estilo_seccion))  # Sección documentos

    tabla_documentos = Table([
        ['Acta de nacimiento', 'Sí' if inscripcion.acta_nacimiento else 'No'],
        ['Boleta de bautizo', 'Sí' if inscripcion.boleta_bautizo else 'No'],
        ['Boleta de confirmación', 'Sí' if inscripcion.boleta_confirmacion else 'No'],
        ['INE', 'Sí' if inscripcion.ine else 'No'],
        ['Otros documentos', inscripcion.otros_documentos or '-'],
    ], colWidths=[55 * mm, 120 * mm])  # Tabla documentos

    tabla_documentos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fbfcfe')),
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#cfd8e3')),
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#dfe6ef')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))  # Estilos documentos

    elementos.append(tabla_documentos)  # Agrega documentos
    elementos.append(Spacer(1, 10))  # Espacio final

    doc.build(elementos)  # Construye el PDF
    return response  # Devuelve el archivo


# ==============================
# 📤 PDF FORMAL POR GRUPOS
# ==============================

@login_required
@user_passes_test(puede_ver)
def exportar_reporte_grupos_pdf(request):
    inscripciones, query, tipo = obtener_inscripciones_filtradas(request)  # Obtiene lista filtrada

    inscripciones = inscripciones.order_by(
        'grupo_catequesis__numero_grupo',  # Ordena por grupo
        'nombre_completo'  # Luego por nombre
    )  # Esto ayuda a mantener el reporte ordenado

    grupos = agrupar_inscripciones_por_grupo(inscripciones)  # Agrupa por grupo

    response = HttpResponse(content_type='application/pdf')  # Tipo de respuesta PDF
    response['Content-Disposition'] = 'attachment; filename="reporte_inscripciones_por_grupo.pdf"'  # Nombre del archivo

    doc = SimpleDocTemplate(
        response,  # La respuesta será el archivo
        pagesize=landscape(letter),  # Hoja horizontal
        rightMargin=10 * mm,  # Margen derecho
        leftMargin=10 * mm,  # Margen izquierdo
        topMargin=10 * mm,  # Margen superior
        bottomMargin=10 * mm,  # Margen inferior
    )

    elementos = []  # Lista de elementos del PDF
    styles = getSampleStyleSheet()  # Estilos base

    estilo_titulo = ParagraphStyle(
        'TituloReporteFormal',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor('#1f3557'),
        alignment=1,
        spaceAfter=4,
    )  # Título principal centrado

    estilo_subtitulo = ParagraphStyle(
        'SubtituloReporteFormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor('#555555'),
        alignment=1,
        spaceAfter=8,
    )  # Subtítulo centrado

    estilo_grupo = ParagraphStyle(
        'EstiloGrupo',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#1f3557'),
        spaceBefore=8,
        spaceAfter=5,
    )  # Estilo para títulos de grupo

    ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo_parroquia.jpg')  # Ruta del logo

    if os.path.exists(ruta_logo):
        logo = Image(ruta_logo, width=22 * mm, height=22 * mm)  # Carga logo
        logo.hAlign = 'CENTER'  # Centra logo
        elementos.append(logo)  # Agrega logo
        elementos.append(Spacer(1, 3))  # Espacio inferior

    elementos.append(Paragraph('Parroquia Santísima Trinidad', estilo_titulo))  # Encabezado parroquial
    elementos.append(Paragraph('Reporte formal de inscripciones agrupado por grupo', estilo_subtitulo))  # Subtítulo

    texto_filtros = f'Filtro nombre: {query if query else "Sin filtro"} | Sacramento: {tipo if tipo else "Todos"} | Total: {inscripciones.count()}'  # Texto resumen
    elementos.append(Paragraph(texto_filtros, estilo_subtitulo))  # Agrega filtros
    elementos.append(Spacer(1, 4))  # Espacio antes de grupos

    for nombre_grupo, registros in grupos.items():  # Recorre cada grupo
        elementos.append(Paragraph(f'Grupo: {nombre_grupo}', estilo_grupo))  # Título del grupo

        encabezados = [[
            'ID',
            'Tipo',
            'Fecha',
            'Nombre',
            'Teléfono',
            'Edad',
            'Catequista',
            'Lugar',
            'Día',
            'Hora',
            'B',
            'E',
            'C',
            'Acta',
            'INE',
        ]]  # Encabezados de la tabla del grupo

        filas = []  # Lista de filas de ese grupo

        for ins in registros:  # Recorre registros del grupo
            filas.append([
                str(ins.id),
                ins.get_tipo_display(),
                ins.fecha.strftime('%d/%m/%Y') if ins.fecha else '-',
                ins.nombre_completo or '-',
                ins.telefono or '-',
                str(ins.edad or '-'),
                str(ins.catequista) if ins.catequista else '-',
                ins.lugar_clases or '-',
                ins.dia_clases or '-',
                ins.hora_clases or '-',
                'Sí' if ins.bautizo else 'No',
                'Sí' if ins.eucaristia else 'No',
                'Sí' if ins.confirmacion else 'No',
                'Sí' if ins.acta_nacimiento else 'No',
                'Sí' if ins.ine else 'No',
            ])  # Agrega una fila por inscripción

        tabla = Table(
            encabezados + filas,  # Une encabezados y datos
            repeatRows=1,  # Repite encabezado si la tabla se parte
            colWidths=[
                12 * mm,  # ID
                22 * mm,  # Tipo
                20 * mm,  # Fecha
                48 * mm,  # Nombre
                28 * mm,  # Teléfono
                12 * mm,  # Edad
                32 * mm,  # Catequista
                28 * mm,  # Lugar
                20 * mm,  # Día
                25 * mm,  # Hora
                10 * mm,  # B
                10 * mm,  # E
                10 * mm,  # C
                15 * mm,  # Acta
                12 * mm,  # INE
            ]
        )  # Tabla formal del grupo

        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f3557')),  # Fondo encabezado
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Texto blanco en encabezado
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Encabezado en negrita
            ('FONTSIZE', (0, 0), (-1, 0), 8),  # Tamaño encabezado
            ('FONTSIZE', (0, 1), (-1, -1), 7.5),  # Tamaño de datos
            ('GRID', (0, 0), (-1, -1), 0.35, colors.HexColor('#cfd8e3')),  # Cuadrícula
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),  # Zebra
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Alineación arriba
            ('LEFTPADDING', (0, 0), (-1, -1), 3),  # Padding izquierdo
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),  # Padding derecho
            ('TOPPADDING', (0, 0), (-1, -1), 3),  # Padding superior
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),  # Padding inferior
        ]))  # Estilos de la tabla

        elementos.append(tabla)  # Agrega tabla del grupo
        elementos.append(Spacer(1, 7))  # Espacio entre grupos

    elementos.append(Spacer(1, 6))  # Espacio antes del pie
    elementos.append(Paragraph(
        'Documento generado por el sistema parroquial.',
        ParagraphStyle(
            'PieReporteFormal',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=7,
            textColor=colors.HexColor('#666666'),
            alignment=2,
        )
    ))  # Pie del reporte

    doc.build(elementos)  # Construye el PDF final
    return response  # Devuelve el archivo PDF