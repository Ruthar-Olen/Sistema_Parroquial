from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import never_cache
from django.http import JsonResponse

from .models import Catequista, GrupoCatequesis, HorarioCatequesis
from .forms import CatequistaForm, GrupoCatequesisForm, HorarioCatequesisForm


def es_catequesis(user):
    return user.is_superuser or user.groups.filter(name='Coordinacion Catequesis').exists()


@never_cache
@login_required
@user_passes_test(es_catequesis)
def menu_catequesis(request):
    catequistas = Catequista.objects.all().order_by('nombre')
    grupos = GrupoCatequesis.objects.select_related('catequista').all().order_by('numero_grupo')
    horarios = HorarioCatequesis.objects.select_related('grupo').all().order_by('grupo__numero_grupo', 'hora_inicio')

    return render(request, 'catequesis/menu.html', {
        'catequistas': catequistas,
        'grupos': grupos,
        'horarios': horarios,
    })


# =========================
# CATEQUISTAS
# =========================

@never_cache
@login_required
@user_passes_test(es_catequesis)
def lista_catequistas(request):
    catequistas = Catequista.objects.all().order_by('nombre')
    return render(request, 'catequesis/catequistas/lista.html', {
        'catequistas': catequistas
    })


@never_cache
@login_required
@user_passes_test(es_catequesis)
def crear_catequista(request):
    if request.method == 'POST':
        form = CatequistaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_catequistas')
    else:
        form = CatequistaForm()

    return render(request, 'catequesis/catequistas/form.html', {
        'form': form,
        'modo': 'crear'
    })


@never_cache
@login_required
@user_passes_test(es_catequesis)
def editar_catequista(request, pk):
    catequista = get_object_or_404(Catequista, pk=pk)

    if request.method == 'POST':
        form = CatequistaForm(request.POST, instance=catequista)
        if form.is_valid():
            form.save()
            return redirect('lista_catequistas')
    else:
        form = CatequistaForm(instance=catequista)

    return render(request, 'catequesis/catequistas/form.html', {
        'form': form,
        'modo': 'editar',
        'objeto': catequista
    })


@never_cache
@login_required
@user_passes_test(es_catequesis)
def eliminar_catequista(request, pk):
    catequista = get_object_or_404(Catequista, pk=pk)

    if request.method == 'POST':
        catequista.delete()
        return redirect('lista_catequistas')

    return render(request, 'catequesis/catequistas/eliminar.html', {
        'objeto': catequista
    })


# =========================
# GRUPOS
# =========================

@never_cache
@login_required
@user_passes_test(es_catequesis)
def lista_grupos(request):
    grupos = GrupoCatequesis.objects.select_related('catequista').all().order_by('numero_grupo')
    return render(request, 'catequesis/grupos/lista.html', {
        'grupos': grupos
    })


@never_cache
@login_required
@user_passes_test(es_catequesis)
def crear_grupo(request):
    if request.method == 'POST':
        form = GrupoCatequesisForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_grupos')
    else:
        form = GrupoCatequesisForm()

    return render(request, 'catequesis/grupos/form.html', {
        'form': form,
        'modo': 'crear'
    })


@never_cache
@login_required
@user_passes_test(es_catequesis)
def editar_grupo(request, pk):
    grupo = get_object_or_404(GrupoCatequesis, pk=pk)

    if request.method == 'POST':
        form = GrupoCatequesisForm(request.POST, instance=grupo)
        if form.is_valid():
            form.save()
            return redirect('lista_grupos')
    else:
        form = GrupoCatequesisForm(instance=grupo)

    return render(request, 'catequesis/grupos/form.html', {
        'form': form,
        'modo': 'editar',
        'objeto': grupo
    })


@never_cache
@login_required
@user_passes_test(es_catequesis)
def eliminar_grupo(request, pk):
    grupo = get_object_or_404(GrupoCatequesis, pk=pk)

    if request.method == 'POST':
        grupo.delete()
        return redirect('lista_grupos')

    return render(request, 'catequesis/grupos/eliminar.html', {
        'objeto': grupo
    })


# =========================
# HORARIOS
# =========================

@never_cache
@login_required
@user_passes_test(es_catequesis)
def lista_horarios(request):
    horarios = HorarioCatequesis.objects.select_related('grupo').all().order_by('grupo__numero_grupo', 'hora_inicio')
    return render(request, 'catequesis/horarios/lista.html', {
        'horarios': horarios
    })


@never_cache
@login_required
@user_passes_test(es_catequesis)
def crear_horario(request):
    if request.method == 'POST':
        form = HorarioCatequesisForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_horarios')
    else:
        form = HorarioCatequesisForm()

    return render(request, 'catequesis/horarios/form.html', {
        'form': form,
        'modo': 'crear'
    })


@never_cache
@login_required
@user_passes_test(es_catequesis)
def editar_horario(request, pk):
    horario = get_object_or_404(HorarioCatequesis, pk=pk)

    if request.method == 'POST':
        form = HorarioCatequesisForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            return redirect('lista_horarios')
    else:
        form = HorarioCatequesisForm(instance=horario)

    return render(request, 'catequesis/horarios/form.html', {
        'form': form,
        'modo': 'editar',
        'objeto': horario
    })


@never_cache
@login_required
@user_passes_test(es_catequesis)
def eliminar_horario(request, pk):
    horario = get_object_or_404(HorarioCatequesis, pk=pk)

    if request.method == 'POST':
        horario.delete()
        return redirect('lista_horarios')

    return render(request, 'catequesis/horarios/eliminar.html', {
        'objeto': horario
    })


# =========================
# API PARA INSCRIPCIONES
# =========================

@never_cache
@login_required
def grupos_por_catequista(request):
    catequista_id = request.GET.get('catequista_id')
    grupos = []

    if catequista_id:
        grupos_qs = GrupoCatequesis.objects.filter(
            catequista_id=catequista_id
        ).order_by('numero_grupo')

        grupos = [
            {
                'id': grupo.id,
                'nombre': grupo.numero_grupo
            }
            for grupo in grupos_qs
        ]

    return JsonResponse({'grupos': grupos})


@never_cache
@login_required
def horarios_por_grupo(request):
    grupo_id = request.GET.get('grupo_id')
    horarios = []

    if grupo_id:
        horarios_qs = HorarioCatequesis.objects.filter(
            grupo_id=grupo_id
        ).select_related('grupo').order_by('hora_inicio')

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

    return JsonResponse({'horarios': horarios})