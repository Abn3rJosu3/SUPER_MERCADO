import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q

from accounts.decorators import solo_admin, solo_cajero
from .models import Producto, Categoria, Cliente, Venta, DetalleVenta, PedidoDelivery, DetallePedidoDelivery


# ==========================================
# VISTAS DE PUNTO DE VENTA Y PRODUCTOS
# ==========================================

@login_required
def punto_venta(request):
    productos = Producto.objects.filter(activo=True, stock__gt=0)
    clientes = Cliente.objects.all()
    return render(request, 'store/punto_venta.html', {
        'productos': productos,
        'clientes': clientes
    })


@login_required
def lista_productos(request):
    categoria_id = request.GET.get('categoria')
    busqueda = request.GET.get('q', '').strip()

    productos = Producto.objects.filter(activo=True).select_related('categoria')

    # Filtrar por categoría seleccionada
    if categoria_id and categoria_id.isdigit():
        productos = productos.filter(categoria_id=int(categoria_id))

    # Filtrar por nombre o código de barras si el usuario busca algo
    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) | Q(codigo_barras__icontains=busqueda)
        )

    # Ordenar primero por categoría y luego por nombre
    productos = productos.order_by('categoria__nombre', 'nombre')

    categorias = Categoria.objects.all().order_by('nombre')

    context = {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': int(categoria_id) if categoria_id and categoria_id.isdigit() else None,
        'busqueda': busqueda,
        'total_productos': productos.count()
    }

    return render(request, 'store/lista_productos.html', context)


@solo_admin
def crear_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
        categoria_id = request.POST.get('categoria')
        codigo_barras = request.POST.get('codigo_barras')
        
        Producto.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            stock=stock,
            codigo_barras=codigo_barras,
            categoria_id=categoria_id if categoria_id else None
        )
        return redirect('lista_productos')
    
    categorias = Categoria.objects.all()
    return render(request, 'store/crear_producto.html', {'categorias': categorias})


@solo_admin
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.descripcion = request.POST.get('descripcion')
        producto.precio = request.POST.get('precio')
        producto.stock = request.POST.get('stock')
        producto.codigo_barras = request.POST.get('codigo_barras')
        categoria_id = request.POST.get('categoria')
        producto.categoria_id = categoria_id if categoria_id else None
        producto.save()
        return redirect('lista_productos')
    
    categorias = Categoria.objects.all()
    return render(request, 'store/editar_producto.html', {'producto': producto, 'categorias': categorias})


@solo_admin
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.activo = False
        producto.save()
        return redirect('lista_productos')
    return render(request, 'store/eliminar_producto.html', {'producto': producto})


# ==========================================
# APIS Y FACTURACIÓN (PROCESAMIENTO DE VENTAS)
# ==========================================

@login_required
@transaction.atomic
def api_guardar_venta(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        tipo_factura = data.get('tipo_factura', 'cf')
        
        if not items:
            return JsonResponse({'error': 'El carrito está vacío'}, status=400)

        # Determinar el cliente según lo seleccionado en Alpine.js
        cliente = None
        if tipo_factura == 'registrado':
            cliente_id = data.get('cliente_id')
            if cliente_id:
                cliente = Cliente.objects.filter(pk=cliente_id).first()
        elif tipo_factura == 'nuevo':
            nit = data.get('nit_manual', 'CF').strip()
            nombre = data.get('nombre_manual', 'Consumidor Final').strip()
            
            if nit.upper() != 'CF' and nit:
                cliente, _ = Cliente.objects.get_or_create(
                    nit=nit,
                    defaults={'nombre': nombre if nombre else 'Cliente Particular'}
                )
        
        # Si no se eligió cliente o era CF, asignar/crear Consumidor Final
        if not cliente:
            cliente, _ = Cliente.objects.get_or_create(
                nit='CF',
                defaults={'nombre': 'Consumidor Final'}
            )

        total = sum(item['cantidad'] * float(item['precio']) for item in items)
        
        venta = Venta.objects.create(
            cliente=cliente,
            cajero=request.user,
            total=total
        )
        
        for item in items:
            producto = Producto.objects.get(pk=item['id'])
            
            if producto.stock < item['cantidad']:
                raise Exception(f"Stock insuficiente para {producto.nombre}")

            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=item['cantidad'],
                precio_unitario=item['precio']
            )
            
            # Descontar del inventario
            producto.stock -= item['cantidad']
            producto.save()
        
        return JsonResponse({'success': True, 'venta_id': venta.id})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def imprimir_factura(request, venta_id):
    venta = get_object_or_404(Venta, id=venta_id)
    total = float(venta.total)
    subtotal = total / 1.12
    iva = total - subtotal
    
    context = {
        'venta': venta,
        'detalles': venta.detalles.all(),
        'subtotal': round(subtotal, 2),
        'iva': round(iva, 2)
    }
    return render(request, 'store/factura_pdf.html', context)


# ==========================================
# MÓDULO DE GESTIÓN DE CLIENTES
# ==========================================

@login_required
def lista_clientes(request):
    clientes = Cliente.objects.all().order_by('-creado_en')
    return render(request, 'store/lista_clientes.html', {'clientes': clientes})


@login_required
def crear_cliente(request):
    if request.method == 'POST':
        nit = request.POST.get('nit', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        direccion = request.POST.get('direccion', '').strip()
        email = request.POST.get('email', '').strip()

        if Cliente.objects.filter(nit=nit).exists():
            return render(request, 'store/crear_cliente.html', {
                'error': f'El NIT "{nit}" ya está registrado con otro cliente.',
                'datos': request.POST
            })

        Cliente.objects.create(
            nit=nit,
            nombre=nombre,
            telefono=telefono,
            direccion=direccion,
            email=email
        )
        return redirect('lista_clientes')

    return render(request, 'store/crear_cliente.html')


@login_required
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        nit = request.POST.get('nit', '').strip()
        
        if Cliente.objects.filter(nit=nit).exclude(pk=pk).exists():
            return render(request, 'store/editar_cliente.html', {
                'cliente': cliente,
                'error': f'El NIT "{nit}" ya pertenece a otro cliente.'
            })

        cliente.nit = nit
        cliente.nombre = request.POST.get('nombre', '').strip()
        cliente.telefono = request.POST.get('telefono', '').strip()
        cliente.direccion = request.POST.get('direccion', '').strip()
        cliente.email = request.POST.get('email', '').strip()
        cliente.save()

        return redirect('lista_clientes')

    return render(request, 'store/editar_cliente.html', {'cliente': cliente})


@solo_admin
def eliminar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        return redirect('lista_clientes')

    return render(request, 'store/eliminar_cliente.html', {'cliente': cliente})


# ==========================================
# VISTAS Y PROCESAMIENTO DE DELIVERY
# ==========================================

def inicio_tienda(request):
    categoria_id = request.GET.get('categoria')
    busqueda = request.GET.get('q', '').strip()

    productos = Producto.objects.filter(activo=True, stock__gt=0).select_related('categoria')

    if categoria_id and categoria_id.isdigit():
        productos = productos.filter(categoria_id=int(categoria_id))

    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) | Q(codigo_barras__icontains=busqueda)
        )

    categorias = Categoria.objects.all().order_by('nombre')

    return render(request, 'store/public_index.html', {
        'productos': productos,
        'categorias': categorias,
        'categoria_seleccionada': int(categoria_id) if categoria_id and categoria_id.isdigit() else None,
        'busqueda': busqueda,
    })


@transaction.atomic
def api_crear_pedido_delivery(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        nombre = data.get('nombre', '').strip()
        telefono = data.get('telefono', '').strip()
        direccion = data.get('direccion', '').strip()
        notas = data.get('notas', '').strip()

        if not items or not nombre or not telefono or not direccion:
            return JsonResponse({'error': 'Por favor completa todos los campos requeridos.'}, status=400)

        total = sum(item['cantidad'] * float(item['precio']) for item in items)

        pedido = PedidoDelivery.objects.create(
            nombre_cliente=nombre,
            telefono=telefono,
            direccion=direccion,
            notas=notas,
            total=total
        )

        for item in items:
            producto = Producto.objects.get(pk=item['id'])
            DetallePedidoDelivery.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=item['cantidad'],
                precio_unitario=item['precio']
            )

        return JsonResponse({'success': True, 'pedido_id': pedido.id})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def lista_pedidos_delivery(request):
    pedidos = PedidoDelivery.objects.prefetch_related('detalles__producto').order_by('-creado_en')
    return render(request, 'store/pedidos_delivery.html', {'pedidos': pedidos})


@login_required
@transaction.atomic
def cambiar_estado_pedido(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(PedidoDelivery, id=pedido_id)
        nuevo_estado = request.POST.get('estado')
        
        # Validar que el estado sea permitido y que el pedido no haya finalizado previamente
        if nuevo_estado in dict(PedidoDelivery.ESTADOS) and pedido.estado not in ['COMPLETADO', 'CANCELADO', 'Completado', 'Cancelado']:
            
            # Al marcar como Completado, creamos la venta oficial en el sistema
            if nuevo_estado in ['COMPLETADO', 'Completado']:
                
                # 1. Buscar si ya existe un cliente registrado con ese número de teléfono
                cliente = None
                if pedido.telefono:
                    cliente = Cliente.objects.filter(telefono=pedido.telefono).first()

                # 2. Si no existe por teléfono, intentar obtener el registro predeterminado de "Consumidor Final" por NIT
                if not cliente:
                    cliente = Cliente.objects.filter(nit='CF').first()

                # 3. Si tampoco existe el registro 'CF' en la base de datos, crearlo
                if not cliente:
                    cliente, _ = Cliente.objects.get_or_create(
                        nit='CF',
                        defaults={
                            'nombre': pedido.nombre_cliente or 'Consumidor Final',
                            'telefono': pedido.telefono or '',
                            'direccion': pedido.direccion or ''
                        }
                    )

                # Registrar Venta en la base de datos general
                venta = Venta.objects.create(
                    cliente=cliente,
                    cajero=request.user,
                    total=pedido.total
                )

                # Copiar ítems del pedido a DetalleVenta y descontar del inventario
                for detalle in pedido.detalles.all():
                    if detalle.producto.stock < detalle.cantidad:
                        raise Exception(f"Stock insuficiente para {detalle.producto.nombre}")

                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=detalle.producto,
                        cantidad=detalle.cantidad,
                        precio_unitario=detalle.precio_unitario
                    )
                    
                    # Actualizar stock de tienda
                    detalle.producto.stock -= detalle.cantidad
                    detalle.producto.save()

            # Guardar el nuevo estado del pedido
            pedido.estado = nuevo_estado
            pedido.save()

    return redirect('lista_pedidos_delivery')