from django.shortcuts import render, redirect, get_object_or_404
from .forms import InscripcionForm
from .models import Inscripcion
from django.contrib.auth.decorators import login_required, user_passes_test


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
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')

    inscripciones = Inscripcion.objects.all()

    if query:
        inscripciones = inscripciones.filter(nombre_completo__icontains=query)

    if tipo:
        inscripciones = inscripciones.filter(tipo=tipo)

    return render(request, 'sacramentos/lista.html', {
        'inscripciones': inscripciones,
        'query': query,
        'tipo': tipo,
        'puede_editar': puede_crear_editar(request.user),
        'puede_eliminar': puede_eliminar(request.user),
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