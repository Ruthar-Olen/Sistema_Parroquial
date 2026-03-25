from django.contrib.auth.decorators import login_required  # Protege la vista para usuarios autenticados
from django.shortcuts import render  # Permite renderizar templates


@login_required
def editor_oficio(request):
    return render(request, 'oficios/editor.html')  # Renderiza la pantalla inicial del editor