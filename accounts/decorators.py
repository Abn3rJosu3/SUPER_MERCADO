from django.shortcuts import redirect
from functools import wraps

def solo_admin(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.es_admin():
            return view_func(request, *args, **kwargs)
        return redirect('punto_venta')
    return wrapper

def solo_cajero(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.es_cajero():
            return view_func(request, *args, **kwargs)
        return redirect('dashboard_admin')
    return wrapper