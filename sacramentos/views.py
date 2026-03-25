from django.shortcuts import render, redirect, get_object_or_404  # Funciones base para vistas
from django.contrib.auth.decorators import login_required, user_passes_test  # Decoradores de permisos
from django.http import HttpResponse  # Respuesta HTTP para exportaciones
from django.conf import settings  # Acceso a configuración del proyecto
from .forms import InscripcionForm  # Formulario de inscripciones
from .models import Inscripcion  # Modelo principal
import csv  # Librería para CSV
import os  # Librería para rutas de archivos
from openpyxl import Workbook  # Librería para Excel

from reportlab.lib import colors  # Colores para PDF
from reportlab.lib.pagesizes import letter  # Tamaño carta
from reportlab.lib.units import mm  # Unidad milímetros
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle  # Estilos de texto
from reportlab.platypus import (  # Componentes para construir PDF
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
    return user.groups.filter(name='Direccion Parroquial').exists()  # Verifica grupo Dirección

def es_secretaria(user):
    return user.groups.filter(name='Secretaria Parroquial').exists()  # Verifica grupo Secretaría

def es_catequesis(user):
    return user.groups.filter(name='Coordinacion Catequesis').exists()  # Verifica grupo Catequesis

def es_consulta(user):
    return user.groups.filter(name='Consulta').exists()  # Verifica grupo Consulta


def puede_ver(user):
    return (
        user.is_superuser
        or es_direccion(user)
        or es_secretaria(user)
        or es_catequesis(user)
        or es_consulta(user)
    )  # Permiso de visualización

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
    query = request.GET.get('q', '')  # Toma filtro de búsqueda por nombre
    tipo = request.GET.get('tipo', '')  # Toma filtro por sacramento

    inscripciones = Inscripcion.objects.all().order_by('-id')  # Consulta base ordenada

    if query:
        inscripciones = inscripciones.filter(nombre_completo__icontains=query)  # Filtra por nombre

    if tipo:
        inscripciones = inscripciones.filter(tipo=tipo)  # Filtra por tipo

    return inscripciones, query, tipo  # Devuelve resultados y filtros usados


# ==============================
# 📌 VISTAS PRINCIPALES
# ==============================

@login_required
@user_passes_test(puede_crear_editar)
def crear_inscripcion(request):
    if request.method == 'POST':
        form = InscripcionForm(request.POST)  # Carga formulario con datos enviados
        if form.is_valid():
            form.save()  # Guarda el registro
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
    inscripciones, query, tipo = obtener_inscripciones_filtradas(request)  # Obtiene filtros aplicados

    return render(request, 'sacramentos/lista.html', {
        'inscripciones': inscripciones,
        'query': query,
        'tipo': tipo,
        'puede_editar': puede_crear_editar(request.user),
        'puede_eliminar': puede_eliminar(request.user),
    })  # Renderiza lista principal


@login_required
@user_passes_test(puede_ver)
def reporte_inscripciones(request):
    inscripciones, query, tipo = obtener_inscripciones_filtradas(request)  # Obtiene datos filtrados

    inscripciones = inscripciones.order_by(
        'grupo_catequesis__numero_grupo',  # Ordena primero por grupo
        'nombre_completo'  # Luego por nombre
    )

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
        form = InscripcionForm(request.POST, instance=inscripcion)  # Carga datos enviados sobre instancia actual
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
    inscripcion = get_object_or_404(Inscripcion, pk=pk)  # Busca el registro

    if request.method == 'POST':
        inscripcion.delete()  # Elimina el registro
        return redirect('lista_inscripciones')  # Regresa a lista

    return render(request, 'sacramentos/eliminar.html', {
        'inscripcion': inscripcion
    })  # Renderiza confirmación de borrado


@login_required
@user_passes_test(puede_ver)
def detalle_inscripcion(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)  # Busca expediente individual

    return render(request, 'sacramentos/detalle.html', {
        'inscripcion': inscripcion,
        'puede_editar': puede_crear_editar(request.user),
    })  # Renderiza vista detalle


# ==============================
# 📤 EXPORTAR CSV
# ==============================

@login_required
@user_passes_test(puede_ver)
def exportar_inscripciones_csv(request):
    inscripciones, query, tipo = obtener_inscripciones_filtradas(request)  # Obtiene lista filtrada

    response = HttpResponse(content_type='text/csv; charset=utf-8')  # Define tipo CSV
    response['Content-Disposition'] = 'attachment; filename="inscripciones.csv"'  # Nombre del archivo

    response.write('\ufeff')  # BOM para compatibilidad con Excel
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
    ])  # Escribe encabezados

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
        ])  # Escribe cada fila

    return response  # Devuelve archivo CSV


# ==============================
# 📤 EXPORTAR EXCEL
# ==============================

@login_required
@user_passes_test(puede_ver)
def exportar_inscripciones_excel(request):
    inscripciones, query, tipo = obtener_inscripciones_filtradas(request)  # Obtiene lista filtrada

    wb = Workbook()  # Crea libro Excel
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
        ])  # Inserta cada registro

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )  # Tipo de archivo Excel
    response['Content-Disposition'] = 'attachment; filename="inscripciones.xlsx"'  # Nombre del archivo

    wb.save(response)  # Guarda el libro en la respuesta
    return response  # Devuelve archivo Excel


# ==============================
# 📤 PDF BONITO DE EXPEDIENTE
# ==============================

@login_required
@user_passes_test(puede_ver)
def exportar_expediente_pdf(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)  # Busca la inscripción por ID

    response = HttpResponse(content_type='application/pdf')  # Define respuesta PDF
    response['Content-Disposition'] = f'attachment; filename="expediente_{inscripcion.id}.pdf"'  # Nombre del archivo

    doc = SimpleDocTemplate(
        response,  # La respuesta será el archivo final
        pagesize=letter,  # Tamaño carta vertical
        rightMargin=14 * mm,  # Margen derecho
        leftMargin=14 * mm,  # Margen izquierdo
        topMargin=12 * mm,  # Margen superior
        bottomMargin=12 * mm,  # Margen inferior
    )

    elementos = []  # Lista de elementos del PDF
    styles = getSampleStyleSheet()  # Estilos base de reportlab

    estilo_titulo = ParagraphStyle(
        'TituloParroquia',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor('#1f3557'),
        spaceAfter=6,
        alignment=1,
    )  # Estilo para título principal

    estilo_subtitulo = ParagraphStyle(
        'SubtituloParroquia',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=colors.HexColor('#555555'),
        spaceAfter=10,
        alignment=1,
    )  # Estilo para subtítulo

    estilo_seccion = ParagraphStyle(
        'SeccionParroquia',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.HexColor('#1f3557'),
        spaceBefore=8,
        spaceAfter=6,
    )  # Estilo para encabezados de sección

    estilo_celda = ParagraphStyle(
        'CeldaParroquia',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.black,
    )  # Estilo para contenido de celdas

    # ===== LOGO =====
    ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo_parroquia.jpg')  # Construye ruta física del logo

    if os.path.exists(ruta_logo):
        logo = Image(ruta_logo, width=28 * mm, height=28 * mm)  # Carga el logo si existe
        logo.hAlign = 'CENTER'  # Centra el logo
        elementos.append(logo)  # Agrega el logo al PDF
        elementos.append(Spacer(1, 4))  # Espacio debajo del logo

    # ===== ENCABEZADO =====
    elementos.append(Paragraph('Parroquia Santísima Trinidad', estilo_titulo))  # Nombre de parroquia
    elementos.append(Paragraph('Expediente de inscripción sacramental', estilo_subtitulo))  # Subtítulo
    elementos.append(Spacer(1, 4))  # Espacio adicional

    # ===== DATOS GENERALES =====
    elementos.append(Paragraph('Datos generales', estilo_seccion))  # Título de sección

    tabla_generales = Table([
        ['ID', str(inscripcion.id), 'Fecha', inscripcion.fecha.strftime('%d/%m/%Y') if inscripcion.fecha else '-'],
        ['Nombre completo', inscripcion.nombre_completo or '-', 'Sacramento', inscripcion.get_tipo_display()],
        ['Teléfono', inscripcion.telefono or '-', 'Edad', str(inscripcion.edad or '-')],
    ], colWidths=[35 * mm, 55 * mm, 35 * mm, 50 * mm])  # Tabla de datos generales

    tabla_generales.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fbfcfe')),  # Fondo claro
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#cfd8e3')),  # Borde externo
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#dfe6ef')),  # Líneas internas
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),  # Fuente base
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Etiquetas columna 1
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),  # Etiquetas columna 3
        ('FONTSIZE', (0, 0), (-1, -1), 9),  # Tamaño de letra
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Alineación arriba
        ('PADDING', (0, 0), (-1, -1), 6),  # Padding interno
    ]))  # Estilo de tabla general

    elementos.append(tabla_generales)  # Agrega tabla al PDF

    # ===== FAMILIA =====
    elementos.append(Paragraph('Familia y vínculos', estilo_seccion))  # Título sección familia

    tabla_familia = Table([
        ['Padre', inscripcion.nombre_padre or '-', 'Madre', inscripcion.nombre_madre or '-'],
        ['Padrino', inscripcion.nombre_padrino or '-', 'Madrina', inscripcion.nombre_madrina or '-'],
    ], colWidths=[35 * mm, 55 * mm, 35 * mm, 50 * mm])  # Tabla de familia

    tabla_familia.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),  # Fondo blanco
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#cfd8e3')),  # Borde externo
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#dfe6ef')),  # Líneas internas
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Etiquetas izquierda
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),  # Etiquetas derecha
        ('FONTSIZE', (0, 0), (-1, -1), 9),  # Tamaño de letra
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Alineación vertical
        ('PADDING', (0, 0), (-1, -1), 6),  # Espaciado interno
    ]))  # Estilo de tabla familia

    elementos.append(tabla_familia)  # Agrega tabla familia

    # ===== CATEQUESIS =====
    elementos.append(Paragraph('Catequesis', estilo_seccion))  # Título sección catequesis

    tabla_catequesis = Table([
        ['Catequista', str(inscripcion.catequista) if inscripcion.catequista else '-', 'Grupo', str(inscripcion.grupo_catequesis) if inscripcion.grupo_catequesis else '-'],
        ['Lugar', inscripcion.lugar_clases or '-', 'Día', inscripcion.dia_clases or '-'],
        ['Hora', inscripcion.hora_clases or '-', '', ''],
    ], colWidths=[35 * mm, 55 * mm, 35 * mm, 50 * mm])  # Tabla catequesis

    tabla_catequesis.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fbfcfe')),  # Fondo suave
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#cfd8e3')),  # Borde externo
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#dfe6ef')),  # Líneas internas
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Etiquetas izquierda
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),  # Etiquetas derecha
        ('FONTSIZE', (0, 0), (-1, -1), 9),  # Tamaño de texto
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Alineación vertical
        ('PADDING', (0, 0), (-1, -1), 6),  # Padding
    ]))  # Estilo de tabla catequesis

    elementos.append(tabla_catequesis)  # Agrega tabla catequesis

    # ===== HISTORIAL SACRAMENTAL =====
    elementos.append(Paragraph('Historial sacramental', estilo_seccion))  # Título historial

    tabla_historial = Table([
        ['Bautizo', 'Sí' if inscripcion.bautizo else 'No', 'Eucaristía', 'Sí' if inscripcion.eucaristia else 'No'],
        ['Confirmación', 'Sí' if inscripcion.confirmacion else 'No', 'Matrimonio', 'Sí' if inscripcion.matrimonio else 'No'],
    ], colWidths=[35 * mm, 20 * mm, 35 * mm, 20 * mm])  # Tabla historial

    tabla_historial.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),  # Fondo blanco
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#cfd8e3')),  # Borde externo
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#dfe6ef')),  # Líneas internas
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Etiquetas columna 1
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),  # Etiquetas columna 3
        ('FONTSIZE', (0, 0), (-1, -1), 9),  # Tamaño texto
        ('PADDING', (0, 0), (-1, -1), 6),  # Padding
    ]))  # Estilo historial

    elementos.append(tabla_historial)  # Agrega historial

    # ===== DOCUMENTOS =====
    elementos.append(Paragraph('Documentos entregados', estilo_seccion))  # Título documentos

    tabla_documentos = Table([
        ['Acta de nacimiento', 'Sí' if inscripcion.acta_nacimiento else 'No'],
        ['Boleta de bautizo', 'Sí' if inscripcion.boleta_bautizo else 'No'],
        ['Boleta de confirmación', 'Sí' if inscripcion.boleta_confirmacion else 'No'],
        ['INE', 'Sí' if inscripcion.ine else 'No'],
        ['Otros documentos', inscripcion.otros_documentos or '-'],
    ], colWidths=[55 * mm, 120 * mm])  # Tabla de documentos

    tabla_documentos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fbfcfe')),  # Fondo claro
        ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#cfd8e3')),  # Borde externo
        ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#dfe6ef')),  # Líneas internas
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),  # Etiquetas en negrita
        ('FONTSIZE', (0, 0), (-1, -1), 9),  # Tamaño texto
        ('PADDING', (0, 0), (-1, -1), 6),  # Padding
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Alineación
    ]))  # Estilo documentos

    elementos.append(tabla_documentos)  # Agrega documentos
    elementos.append(Spacer(1, 10))  # Espacio final

    # ===== PIE =====
    elementos.append(Paragraph(
        f'Folio interno: {inscripcion.id}',
        ParagraphStyle(
            'PieDocumento',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=8,
            textColor=colors.HexColor('#666666'),
            alignment=2,
        )
    ))  # Pie del PDF alineado a la derecha

    doc.build(elementos)  # Construye PDF completo
    return response  # Devuelve el archivo PDF