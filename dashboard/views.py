from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def admin_dashboard(request):
    return render(request, 'dashboard/admin_dashboard.html')


@login_required
def user_dashboard(request):
    return render(request, 'dashboard/user_dashboard.html')


@login_required
def direccion_dashboard(request):
    return render(request, 'dashboard/direccion_dashboard.html')


@login_required
def secretaria_dashboard(request):
    return render(request, 'dashboard/secretaria_dashboard.html')


@login_required
def catequesis_dashboard(request):
    return render(request, 'dashboard/catequesis_dashboard.html')


@login_required
def consulta_dashboard(request):
    return render(request, 'dashboard/consulta_dashboard.html')