from django.db import models


class Catequista(models.Model):
    nombre = models.CharField(max_length=150)

    def __str__(self):
        return self.nombre


class GrupoCatequesis(models.Model):
    numero_grupo = models.CharField(max_length=20)
    catequista = models.ForeignKey(Catequista, on_delete=models.CASCADE, related_name='grupos')
    lugar = models.CharField(max_length=150)
    dia = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.numero_grupo} - {self.catequista.nombre} - {self.dia}"
    
class HorarioCatequesis(models.Model):
    grupo = models.ForeignKey(GrupoCatequesis, on_delete=models.CASCADE, related_name='horarios')
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.grupo.numero_grupo} - {self.hora_inicio.strftime('%H:%M')} a {self.hora_fin.strftime('%H:%M')}"