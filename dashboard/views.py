from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import solo_admin
from store.models import Venta, Producto, Proveedor
from django.utils import timezone
from datetime import timedelta

@solo_admin
def dashboard_admin(request):
    hoy = timezone.now().date()
    inicio_mes = hoy.replace(day=1)
    
    # Ventas del día
    ventas_hoy = Venta.objects.filter(creado_en__date=hoy, estado='completada')
    total_dia = sum(v.total for v in ventas_hoy)
    
    # Ventas del mes
    ventas_mes = Venta.objects.filter(creado_en__date__gte=inicio_mes, estado='completada')
    total_mes = sum(v.total for v in ventas_mes)
    
    # Totales generales
    total_ventas = Venta.objects.filter(estado='completada').count()
    total_productos = Producto.objects.filter(activo=True).count()
    total_proveedores = Proveedor.objects.filter(activo=True).count()
    
    # Últimas 5 ventas
    ultimas_ventas = Venta.objects.filter(estado='completada').order_by('-creado_en')[:5]
    
    return render(request, 'dashboard/admin.html', {
        'total_dia': total_dia,
        'total_mes': total_mes,
        'total_ventas': total_ventas,
        'total_productos': total_productos,
        'total_proveedores': total_proveedores,
        'ultimas_ventas': ultimas_ventas,
    })

@solo_admin
def lista_proveedores(request):
    proveedores = Proveedor.objects.filter(activo=True)
    return render(request, 'dashboard/proveedores.html', {'proveedores': proveedores})

@solo_admin
def crear_proveedor(request):
    if request.method == 'POST':
        Proveedor.objects.create(
            nombre=request.POST.get('nombre'),
            contacto=request.POST.get('contacto'),
            telefono=request.POST.get('telefono'),
            email=request.POST.get('email'),
            direccion=request.POST.get('direccion')
        )
        return redirect('lista_proveedores')
    return render(request, 'dashboard/crear_proveedor.html')

@solo_admin
def editar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        proveedor.nombre = request.POST.get('nombre')
        proveedor.contacto = request.POST.get('contacto')
        proveedor.telefono = request.POST.get('telefono')
        proveedor.email = request.POST.get('email')
        proveedor.direccion = request.POST.get('direccion')
        proveedor.save()
        return redirect('lista_proveedores')
    return render(request, 'dashboard/editar_proveedor.html', {'proveedor': proveedor})

@solo_admin
def eliminar_proveedor(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        proveedor.activo = False
        proveedor.save()
        return redirect('lista_proveedores')
    return render(request, 'dashboard/eliminar_proveedor.html', {'proveedor': proveedor})