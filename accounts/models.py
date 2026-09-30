from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('cajero', 'Cajero'),
    ]
    
    rol = models.CharField(max_length=10, choices=ROL_CHOICES, default='cajero')
    telefono = models.CharField(max_length=20, blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    def es_admin(self):
        return self.rol == 'admin'
    
    def es_cajero(self):
        return self.rol == 'cajero'
    
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'