from django.http import HttpResponse
from django.shortcuts import redirect 
from django.http import Http404 


def unauthenticated_user(function=None, redirect_url='/acceder'):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_url)
                
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)

    return decorator


def usuarios_permitidos(roles_permitidos=[]):
    def decorators(view_func):
        def wrapper_func(request, *args, **kwargs):

            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in roles_permitidos:
                return view_func(request, *args, **kwargs)
            else:
                raise Http404("Página no encontrada")
        return wrapper_func
    return decorators