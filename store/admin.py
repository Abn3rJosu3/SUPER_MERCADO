from django.contrib import admin
from .models import Categoria, Producto, Cliente, Proveedor, Venta, DetalleVenta
from .models import OfertaSlider


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'precio', 'stock', 'categoria', 'activo']
    list_filter = ['categoria', 'activo']
    search_fields = ['nombre', 'codigo_barras']


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['nit', 'nombre', 'telefono']
    search_fields = ['nit', 'nombre']


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'contacto', 'telefono', 'activo']
    list_filter = ['activo']


class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'cajero', 'total', 'estado', 'creado_en']
    list_filter = ['estado', 'creado_en']
    inlines = [DetalleVentaInline]



@admin.register(OfertaSlider)
class OfertaSliderAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'activo', 'orden', 'creado_en')
    list_editable = ('activo', 'orden')
    search_fields = ('titulo', 'descripcion')