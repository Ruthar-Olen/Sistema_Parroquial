from django.contrib.auth.decorators import login_required  # Protege vistas para usuarios autenticados
from django.shortcuts import render, redirect, get_object_or_404  # Permite renderizar, redirigir y buscar objetos
from .models import BienInventario, AreaInventario, EstadoInventario  # Importa modelos del módulo
from .forms import BienInventarioForm  # Importa el formulario del inventario


@login_required
def lista_bienes(request):
    query = request.GET.get('q', '').strip()  # Obtiene el texto de búsqueda
    area_id = request.GET.get('area', '').strip()  # Obtiene el área seleccionada
    estado_id = request.GET.get('estado', '').strip()  # Obtiene el estado seleccionado

    bienes = BienInventario.objects.filter(activo=True).select_related('area', 'estado').order_by('-fecha_alta')
    # Obtiene bienes activos
    # select_related mejora rendimiento trayendo área y estado en la misma consulta
    # ordena por fecha de alta más reciente

    if query:
        bienes = bienes.filter(descripcion__icontains=query)
        # Filtra por coincidencia en la descripción del bien

    if area_id:
        bienes = bienes.filter(area_id=area_id)
        # Filtra por área si se seleccionó una

    if estado_id:
        bienes = bienes.filter(estado_id=estado_id)
        # Filtra por estado si se seleccionó uno

    areas = AreaInventario.objects.filter(activa=True).order_by('nombre')
    # Obtiene áreas activas para el filtro

    estados = EstadoInventario.objects.filter(activo=True).order_by('nombre')
    # Obtiene estados activos para el filtro

    return render(request, 'inventario/lista.html', {
        'bienes': bienes,  # Lista de bienes filtrados
        'areas': areas,  # Áreas para el filtro
        'estados': estados,  # Estados para el filtro
        'query': query,  # Valor actual del buscador
        'area_id': area_id,  # Valor actual del filtro área
        'estado_id': estado_id,  # Valor actual del filtro estado
    })


@login_required
def crear_bien(request):
    if request.method == 'POST':
        form = BienInventarioForm(request.POST, request.FILES)
        # Carga el formulario con datos enviados y archivos subidos

        if form.is_valid():
            form.save()
            # Guarda el bien
            # El código se genera automáticamente en el modelo

            return redirect('lista_bienes')
            # Regresa a la lista después de guardar
    else:
        form = BienInventarioForm()
        # Si no es POST, muestra formulario vacío

    return render(request, 'inventario/crear.html', {
        'form': form,  # Envía el formulario al template
        'modo': 'crear',  # Indica modo crear
        'bien': None,  # No hay bien previo en creación
    })


@login_required
def editar_bien(request, pk):
    bien = get_object_or_404(BienInventario, pk=pk, activo=True)
    # Busca el bien por ID y solo permite editar si sigue activo

    if request.method == 'POST':
        form = BienInventarioForm(request.POST, request.FILES, instance=bien)
        # Carga el formulario con datos enviados y la instancia actual

        if form.is_valid():
            form.save()
            # Guarda los cambios sobre el mismo bien

            return redirect('lista_bienes')
            # Regresa a la lista después de guardar
    else:
        form = BienInventarioForm(instance=bien)
        # Si no es POST, muestra el formulario lleno con los datos actuales

    return render(request, 'inventario/crear.html', {
        'form': form,  # Envía el formulario al template
        'modo': 'editar',  # Indica modo editar
        'bien': bien,  # Envía el bien actual para mostrar código o imagen
    })


@login_required
def baja_bien(request, pk):
    bien = get_object_or_404(BienInventario, pk=pk, activo=True)
    # Busca el bien por ID
    # Solo permite dar de baja bienes que siguen activos

    if request.method == 'POST':
        estado_baja = EstadoInventario.objects.filter(nombre__iexact='Baja').first()
        # Busca un estado llamado "Baja" sin importar mayúsculas/minúsculas

        bien.activo = False
        # Marca el bien como inactivo para que ya no aparezca en la lista normal

        if estado_baja:
            bien.estado = estado_baja
            # Si existe el estado "Baja", lo asigna automáticamente

        bien.save()
        # Guarda el cambio

        return redirect('lista_bienes')
        # Regresa a la lista después de dar de baja

    return render(request, 'inventario/baja.html', {
        'bien': bien,  # Envía el bien al template de confirmación
    })