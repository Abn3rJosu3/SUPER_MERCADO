from django.db import models
from django.contrib.auth import get_user_model


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = 'categorias'


class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    codigo_barras = models.CharField(max_length=50, unique=True, blank=True, null=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = 'productos'
        ordering = ['nombre']


class Cliente(models.Model):
    nit = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} (NIT: {self.nit})"
    
    class Meta:
        db_table = 'clientes'


class Proveedor(models.Model):
    nombre = models.CharField(max_length=200)
    contacto = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        db_table = 'proveedores'


class Venta(models.Model):
    ESTADO_CHOICES = [
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('pendiente', 'Pendiente'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True)
    cajero = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='completada')
    creado_en = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Venta #{self.id} - {self.total}"
    
    class Meta:
        db_table = 'ventas'
        ordering = ['-creado_en']


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario
    
    class Meta:
        db_table = 'detalles_venta'

class OfertaSlider(models.Model):
    titulo = models.CharField(max_length=150, help_text="Título de la oferta")
    descripcion = models.TextField(blank=True, null=True, help_text="Descripción o condiciones breve")
    imagen = models.ImageField(upload_to='ofertas/', help_text="Imagen del banner publicitario")
    activo = models.BooleanField(default=True, help_text="Marcar para mostrar en el login")
    orden = models.PositiveIntegerField(default=0, help_text="Orden de aparición (menor a mayor)")
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.titulo

    class Meta:
        db_table = 'ofertas_slider'
        ordering = ['orden', '-creado_en']

User = get_user_model()

class PedidoDelivery(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('DESPACHADO', 'En camino / Despachado'),
        ('COMPLETADO', 'Entregado / Completado'),
        ('CANCELADO', 'Cancelado'),
    ]

    nombre_cliente = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    notas = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.nombre_cliente} ({self.estado})"

class DetallePedidoDelivery(models.Model):
    pedido = models.ForeignKey(PedidoDelivery, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio_unitario    