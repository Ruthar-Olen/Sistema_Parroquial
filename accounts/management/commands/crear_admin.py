from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = "Crea un superusuario automatico"
    
    def handle(self, *args, **kwargs):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@mail.com',
                password='admin123'
    
            )
            self.stdout.write(self.style.SUCCESS('Superusuario creado'))
        else:
            self.stdout.write('El superusuario ya existe')