from django.urls import path
from . import views

urlpatterns = [
    path('', views.punto_venta, name='punto_venta'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/nuevo/', views.crear_producto, name='crear_producto'),
    path('productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    path('api/guardar-venta/', views.api_guardar_venta, name='guardar_venta'),
    path('factura/<int:venta_id>/', views.imprimir_factura, name='imprimir_factura'),
    path('clientes/', views.lista_clientes, name='lista_clientes'),
    path('clientes/crear/', views.crear_cliente, name='crear_cliente'),
    path('clientes/editar/<int:pk>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/eliminar/<int:pk>/', views.eliminar_cliente, name='eliminar_cliente'),
    path('pedidos-delivery/cambiar-estado/<int:pedido_id>/', views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
]