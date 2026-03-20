from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


@login_required
def redirect_user(request):
    user = request.user

    # Superadministrador técnico
    if user.is_superuser:
        return redirect('admin_dashboard')

    # Dirección parroquial
    if user.groups.filter(name='Direccion Parroquial').exists():
        return redirect('direccion_dashboard')

    # Secretaría parroquial
    if user.groups.filter(name='Secretaria Parroquial').exists():
        return redirect('secretaria_dashboard')

    # Coordinación de catequesis
    if user.groups.filter(name='Coordinacion Catequesis').exists():
        return redirect('catequesis_dashboard')

    # Consulta
    if user.groups.filter(name='Consulta').exists():
        return redirect('consulta_dashboard')

    return redirect('user_dashboard')