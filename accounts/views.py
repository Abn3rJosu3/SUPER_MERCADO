from django.shortcuts import render

# Create your views here.
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from store.models import OfertaSlider

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ofertas'] = OfertaSlider.objects.filter(activo=True)
        return context


@login_required
def redireccionar_dashboard(request):
    """Redirige según el rol después del login"""
    if request.user.es_admin():
        return redirect('dashboard_admin')
    else:
        return redirect('punto_venta')

    from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)
    return redirect('login')