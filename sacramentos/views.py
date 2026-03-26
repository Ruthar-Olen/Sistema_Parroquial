from django.shortcuts import render, redirect, get_object_or_404  # Funciones base para vistas
from django.contrib.auth.decorators import login_required, user_passes_test  # Decoradores de permisos
from django.http import HttpResponse  # Respuesta HTTP para exportaciones
from django.conf import settings  # Acceso a la configuración del proyecto
from django.templatetags.static import static  # Permite construir la URL de archivos estáticos
from .forms import InscripcionForm  # Formulario de inscripciones
from .models import Inscripcion  # Modelo principal
import csv  # Librería para CSV
import os  # Librería para manejar rutas
from collections import OrderedDict  # Estructura ordenada para agrupar por grupo
from openpyxl import Workbook  # Librería para Excel

from django.template.loader import render_to_string  # Permite renderizar templates a texto HTML
from weasyprint import HTML, CSS  # Herramientas para convertir HTML a PDF
from catequesis.models import FormatoTipo, FormatoCatequesis  # Modelos de formatos configurables

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


def puede_generar_formatos(user):
    return (
        user.is_superuser
        or es_direccion(user)
        or es_secretaria(user)
    )  # Permiso para generar formatos PDF desde sacramentos


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
        'puede_generar_formatos': puede_generar_formatos(request.user),
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


@login_required
@user_passes_test(puede_generar_formatos)
def seleccionar_formato_inscripcion(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)  # Busca la inscripción seleccionada

    if not inscripcion.grupo_catequesis:
        return render(request, 'sacramentos/formato_bloqueado.html', {
            'inscripcion': inscripcion,
            'motivo': 'La inscripción no tiene grupo asignado. No se puede generar ningún formato hasta capturar el grupo.'
        })
        # Bloquea la generación si la inscripción no tiene grupo asignado

    tipos_formato = FormatoTipo.objects.filter(activo=True).order_by('nombre')
    # Obtiene los tipos de formato activos que pueden mostrarse como opción

    return render(request, 'sacramentos/seleccionar_formato.html', {
        'inscripcion': inscripcion,
        'tipos_formato': tipos_formato,
    })
    # Renderiza la pantalla para elegir qué formato se imprimirá


@login_required
@user_passes_test(puede_generar_formatos)
def generar_formato_pdf(request, pk, clave_tipo):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)  # Busca la inscripción seleccionada

    if not inscripcion.grupo_catequesis:
        return render(request, 'sacramentos/formato_bloqueado.html', {
            'inscripcion': inscripcion,
            'motivo': 'La inscripción no tiene grupo asignado. No se puede generar ningún formato hasta capturar el grupo.'
        })
        # Bloquea la generación si no existe grupo asignado

    tipo_formato = get_object_or_404(
        FormatoTipo,
        clave=clave_tipo.upper(),
        activo=True
    )  # Busca el tipo de formato solicitado por su clave

    formato = get_object_or_404(
        FormatoCatequesis,
        tipo=tipo_formato,
        activo=True
    )  # Busca el formato activo correspondiente a ese tipo

    nombre_mayusculas = (inscripcion.nombre_completo or '').upper()
    # Convierte el nombre completo a mayúsculas para impresión formal

    grupo_impresion = inscripcion.grupo_catequesis.numero_grupo.upper()
    # Toma el número de grupo en formato corto, por ejemplo 1A o 3C

    celdas = formato.celdas.all().order_by('fila', 'columna')
    # Obtiene las celdas del formato en orden natural

    max_fila = 0  # Inicializa fila máxima
    max_columna = 0  # Inicializa columna máxima

    for celda in celdas:
        if celda.fila > max_fila:
            max_fila = celda.fila
            # Guarda el mayor número de fila encontrado

        if celda.columna > max_columna:
            max_columna = celda.columna
            # Guarda el mayor número de columna encontrado

    matriz_celdas = []
    # Aquí se construirá la cuadrícula completa que usará el template

    if formato.usa_celdas and max_fila > 0 and max_columna > 0:
        mapa_celdas = {
            (celda.fila, celda.columna): celda.contenido
            for celda in celdas
        }
        # Convierte las celdas a un diccionario para ubicarlas rápidamente por fila y columna

        for fila in range(1, max_fila + 1):
            fila_actual = []
            # Crea una fila vacía de trabajo

            for columna in range(1, max_columna + 1):
                fila_actual.append(mapa_celdas.get((fila, columna), ''))
                # Inserta el contenido de la celda o texto vacío si no existe

            matriz_celdas.append(fila_actual)
            # Agrega la fila completa a la matriz final

    template_pdf = 'sacramentos/formatos/nino.html'
    # Define el template por defecto para el formato de niño

    if tipo_formato.clave.upper() == 'PAPAS':
        template_pdf = 'sacramentos/formatos/papas.html'
        # Usa el template de papás cuando se solicite ese tipo

    elif tipo_formato.clave.upper() == 'TARJETON':
        template_pdf = 'sacramentos/formatos/tarjeton.html'
        # Usa el template de tarjetón cuando se solicite ese tipo

    url_logo_fondo = request.build_absolute_uri(static('img/logo_parroquia.jpg'))
    # Construye la URL absoluta de la imagen de fondo para que WeasyPrint sí pueda cargarla

    html_string = render_to_string(template_pdf, {
        'inscripcion': inscripcion,
        'formato': formato,
        'nombre_impresion': nombre_mayusculas,
        'grupo_impresion': grupo_impresion,
        'matriz_celdas': matriz_celdas,
        'tipo_formato': tipo_formato,
        'url_logo_fondo': url_logo_fondo,
    }, request=request)
    # Renderiza el template HTML que servirá como base para el PDF
    # También envía la URL absoluta del fondo

    response = HttpResponse(content_type='application/pdf')
    # Define que la respuesta será un archivo PDF

    response['Content-Disposition'] = (
        f'inline; filename="formato_{tipo_formato.clave.lower()}_{inscripcion.id}.pdf"'
    )
    # Muestra el PDF en navegador y le asigna un nombre de archivo coherente

    html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
    # Construye el documento HTML resolviendo correctamente rutas de imágenes y archivos estáticos

    css_impresion = CSS(string='''
        @page {
            size: letter;
            margin: 10mm;
        }
    ''')
    # Define una hoja tamaño carta con márgenes estables para impresión

    html.write_pdf(response, stylesheets=[css_impresion])
    # Convierte el HTML a PDF y lo escribe directamente en la respuesta

    return response
    # Devuelve el PDF generado al navegador


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
    )  # Mantiene orden lógico para el reporte

    grupos = agrupar_inscripciones_por_grupo(inscripciones)  # Agrupa registros por grupo

    response = HttpResponse(content_type='application/pdf')  # Define respuesta PDF
    response['Content-Disposition'] = 'attachment; filename="reporte_inscripciones_por_grupo.pdf"'  # Nombre del archivo

    doc = SimpleDocTemplate(
        response,  # La salida será el archivo descargable
        pagesize=landscape(letter),  # Fuerza hoja horizontal
        rightMargin=6 * mm,  # Margen derecho pequeño para aprovechar ancho
        leftMargin=6 * mm,  # Margen izquierdo pequeño
        topMargin=8 * mm,  # Margen superior
        bottomMargin=8 * mm,  # Margen inferior
    )

    elementos = []  # Lista de elementos del PDF
    styles = getSampleStyleSheet()  # Estilos base

    estilo_titulo = ParagraphStyle(
        'TituloReporteFormal',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=15,
        textColor=colors.HexColor('#1f3557'),
        alignment=1,
        spaceAfter=3,
    )  # Estilo del título principal

    estilo_subtitulo = ParagraphStyle(
        'SubtituloReporteFormal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        textColor=colors.HexColor('#555555'),
        alignment=1,
        spaceAfter=6,
    )  # Estilo del subtítulo y filtros

    estilo_grupo = ParagraphStyle(
        'EstiloGrupo',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.HexColor('#1f3557'),
        spaceBefore=6,
        spaceAfter=4,
    )  # Estilo para encabezado de cada grupo

    estilo_celda = ParagraphStyle(
        'EstiloCeldaCompacta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.5,
        leading=7.2,
        textColor=colors.black,
    )  # Estilo de celdas para permitir saltos de línea

    estilo_celda_bold = ParagraphStyle(
        'EstiloCeldaBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=6.5,
        leading=7.2,
        textColor=colors.white,
        alignment=1,
    )  # Estilo para encabezados centrados

    ruta_logo = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo_parroquia.jpg')  # Ruta física del logo

    if os.path.exists(ruta_logo):
        logo = Image(ruta_logo, width=18 * mm, height=18 * mm)  # Logo más compacto
        logo.hAlign = 'CENTER'  # Centra el logo
        elementos.append(logo)  # Agrega logo al PDF
        elementos.append(Spacer(1, 2))  # Espacio debajo del logo

    elementos.append(Paragraph('Parroquia Santísima Trinidad', estilo_titulo))  # Nombre de la parroquia
    elementos.append(Paragraph('Reporte formal de inscripciones agrupado por grupo', estilo_subtitulo))  # Título del documento

    texto_filtros = (
        f'Filtro nombre: {query if query else "Sin filtro"}'
        f' | Sacramento: {tipo if tipo else "Todos"}'
        f' | Total: {inscripciones.count()}'
    )  # Texto de filtros activos
    elementos.append(Paragraph(texto_filtros, estilo_subtitulo))  # Agrega filtros
    elementos.append(Spacer(1, 3))  # Espacio antes de grupos

    anchos_columnas = [
        10 * mm,  # ID
        16 * mm,  # Tipo
        16 * mm,  # Fecha
        34 * mm,  # Nombre
        20 * mm,  # Teléfono
        9 * mm,   # Edad
        26 * mm,  # Catequista
        20 * mm,  # Lugar
        14 * mm,  # Día
        16 * mm,  # Hora
        7 * mm,   # B
        7 * mm,   # E
        7 * mm,   # C
        9 * mm,   # Acta
        7 * mm,   # INE
        20 * mm,  # Otros
    ]  # Reparto compacto del ancho

    for nombre_grupo, registros in grupos.items():
        elementos.append(Paragraph(f'Grupo: {nombre_grupo}', estilo_grupo))  # Título del grupo
        elementos.append(Paragraph(f'Registros en este grupo: {len(registros)}', estilo_subtitulo))  # Cantidad del grupo

        encabezados = [[
            Paragraph('ID', estilo_celda_bold),  # Encabezado ID
            Paragraph('Tipo', estilo_celda_bold),  # Encabezado Tipo
            Paragraph('Fecha', estilo_celda_bold),  # Encabezado Fecha
            Paragraph('Nombre', estilo_celda_bold),  # Encabezado Nombre
            Paragraph('Teléfono', estilo_celda_bold),  # Encabezado Teléfono
            Paragraph('Edad', estilo_celda_bold),  # Encabezado Edad
            Paragraph('Catequista', estilo_celda_bold),  # Encabezado Catequista
            Paragraph('Lugar', estilo_celda_bold),  # Encabezado Lugar
            Paragraph('Día', estilo_celda_bold),  # Encabezado Día
            Paragraph('Hora', estilo_celda_bold),  # Encabezado Hora
            Paragraph('B', estilo_celda_bold),  # Bautizo
            Paragraph('E', estilo_celda_bold),  # Eucaristía
            Paragraph('C', estilo_celda_bold),  # Confirmación
            Paragraph('Acta', estilo_celda_bold),  # Acta
            Paragraph('INE', estilo_celda_bold),  # INE
            Paragraph('Otros', estilo_celda_bold),  # Otros documentos
        ]]  # Encabezados de tabla

        filas = []  # Contenedor de filas

        for ins in registros:
            filas.append([
                Paragraph(str(ins.id), estilo_celda),  # ID
                Paragraph(ins.get_tipo_display() or '-', estilo_celda),  # Tipo
                Paragraph(ins.fecha.strftime('%d/%m/%Y') if ins.fecha else '-', estilo_celda),  # Fecha
                Paragraph(ins.nombre_completo or '-', estilo_celda),  # Nombre completo
                Paragraph(ins.telefono or '-', estilo_celda),  # Teléfono
                Paragraph(str(ins.edad or '-'), estilo_celda),  # Edad
                Paragraph(str(ins.catequista) if ins.catequista else '-', estilo_celda),  # Catequista
                Paragraph(ins.lugar_clases or '-', estilo_celda),  # Lugar
                Paragraph(ins.dia_clases or '-', estilo_celda),  # Día
                Paragraph(ins.hora_clases or '-', estilo_celda),  # Hora
                Paragraph('Sí' if ins.bautizo else 'No', estilo_celda),  # Bautizo
                Paragraph('Sí' if ins.eucaristia else 'No', estilo_celda),  # Eucaristía
                Paragraph('Sí' if ins.confirmacion else 'No', estilo_celda),  # Confirmación
                Paragraph('Sí' if ins.acta_nacimiento else 'No', estilo_celda),  # Acta
                Paragraph('Sí' if ins.ine else 'No', estilo_celda),  # INE
                Paragraph(ins.otros_documentos or '-', estilo_celda),  # Otros documentos
            ])  # Fila completa por inscripción

        tabla = Table(
            encabezados + filas,  # Une encabezados y contenido
            repeatRows=1,  # Repite encabezado si parte página
            colWidths=anchos_columnas,  # Usa anchos compactos definidos arriba
        )

        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f3557')),  # Fondo azul en encabezado
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),  # Texto blanco encabezado
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Negrita encabezado
            ('FONTSIZE', (0, 0), (-1, 0), 6.5),  # Tamaño encabezado
            ('FONTSIZE', (0, 1), (-1, -1), 6.5),  # Tamaño filas
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#cfd8e3')),  # Cuadrícula suave
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),  # Zebra
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Alinea arriba
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Centra ID
            ('ALIGN', (4, 0), (5, -1), 'CENTER'),  # Centra teléfono y edad
            ('ALIGN', (10, 0), (14, -1), 'CENTER'),  # Centra checks
            ('LEFTPADDING', (0, 0), (-1, -1), 2.5),  # Padding izquierdo reducido
            ('RIGHTPADDING', (0, 0), (-1, -1), 2.5),  # Padding derecho reducido
            ('TOPPADDING', (0, 0), (-1, -1), 2),  # Padding superior reducido
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),  # Padding inferior reducido
        ]))  # Estilos generales de tabla

        elementos.append(tabla)  # Agrega tabla del grupo al documento
        elementos.append(Spacer(1, 5))  # Espacio entre grupos

    elementos.append(Spacer(1, 4))  # Espacio antes del pie
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
    ))  # Pie del documento

    doc.build(elementos)  # Construye PDF final
    return response  # Devuelve archivo PDF