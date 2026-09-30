from django.urls import path
from . import views
from store import views as store_views

urlpatterns = [
    # Rutas de Autenticación (Accounts)
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('redireccion/', views.redireccionar_dashboard, name='redireccionar'),
    
    # Rutas Públicas y de Pedidos Delivery (Store)
    path('', store_views.inicio_tienda, name='home'),
    path('api/pedidos/crear/', store_views.api_crear_pedido_delivery, name='api_crear_pedido'),
    path('pedidos-delivery/', store_views.lista_pedidos_delivery, name='lista_pedidos_delivery'),
    path('pedidos-delivery/<int:pedido_id>/estado/', store_views.cambiar_estado_pedido, name='cambiar_estado_pedido'),
]