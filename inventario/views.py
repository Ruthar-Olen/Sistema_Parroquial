from django.contrib.auth.decorators import login_required  # Protege vistas para usuarios autenticados
from django.shortcuts import render, redirect  # Permite renderizar templates y redirigir
from .models import BienInventario  # Importa el modelo de bienes
from .forms import BienInventarioForm  # Importa el formulario del inventario


@login_required
def lista_bienes(request):
    bienes = BienInventario.objects.filter(activo=True).select_related('area', 'estado').order_by('-fecha_alta')
    # Obtiene solo bienes activos
    # select_related mejora rendimiento al traer área y estado en la misma consulta
    # ordena por fecha de alta más reciente

    return render(request, 'inventario/lista.html', {
        'bienes': bienes  # Envía los bienes al template
    })


@login_required
def crear_bien(request):
    if request.method == 'POST':
        form = BienInventarioForm(request.POST, request.FILES)
        # Carga el formulario con datos enviados y archivos subidos

        if form.is_valid():
            form.save()
            # Guarda el bien
            # Por ahora se guarda sin código automático, eso lo haremos en el siguiente paso

            return redirect('lista_bienes')
            # Después de guardar, regresa a la lista
    else:
        form = BienInventarioForm()
        # Si no es POST, muestra formulario vacío

    return render(request, 'inventario/crear.html', {
        'form': form,  # Envía el formulario al template
        'modo': 'crear',  # Marca el modo por si luego reutilizamos el template para editar
    })