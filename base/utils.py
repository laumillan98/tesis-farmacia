from django.contrib.admin.models import LogEntry, DELETION,ADDITION,CHANGE
from django.utils.encoding import force_str
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import View
import json


class RequiredSecurityMixin(object):
    """
       @Desc: Comprueba que el usuario este autenticado y que tenga los permisos para acceder a la vista.
       """
    # Code name list
    CREATE = 'add'
    CHANGE = 'change'
    DELETE = 'delete'
    LIST = 'list'

    need_login = False
    permission = None

    def dispatch(self, request, *args, **kwargs):
        if self.need_login and self.permission:
            @login_required
            @permission_required(
                '%s.%s_%s' % (self.model._meta.app_label, self.permission, self.model._meta.model_name),
                raise_exception=True)
            def wrapper(request, *args, **kwargs):
                return super(RequiredSecurityMixin, self).dispatch(request, *args, **kwargs)
        elif self.need_login and not self.permission:
            @login_required
            def wrapper(request, *args, **kwargs):
                return super(RequiredSecurityMixin, self).dispatch(request, *args, **kwargs)
        else:
            def wrapper(request, *args, **kwargs):
                return super(RequiredSecurityMixin, self).dispatch(request, *args, **kwargs)

        return wrapper(request, *args, **kwargs)
    


class BaseDeleteView(SuccessMessageMixin, View):
    """
    @Desc: Vista genérica para la eliminación de objetos
    """

    def get(self, request, *args, **kwargs):
        obj = self.model.objects.get(pk=kwargs['pk'])
        obj.delete()
        register_logs(request, self.model, kwargs['pk'], force_str(obj), DELETION)
        messages.success(self.request, self.success_message.replace('objeto', force_str(obj)))
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        pk_list = json.loads(request.POST.get('items'))
        for item in pk_list:
            obj = self.model.objects.get(pk=item)
            obj.delete()
            register_logs(request, self.model, item, force_str(obj), DELETION)
        messages.success(self.request, 'Se eliminaron satisfactoriamente todos los elementos.')
        return HttpResponseRedirect(self.get_success_url())
    


def obtener_ip(request):
    x_forwarded_for = request.META.get('X-Forwarded-For')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip



def register_logs(request, model, object_id, object_unicode, action):
    """
    @Desc: Funcion utilizada para registrar los logs de las acciones generadas por el usuario
    """
    if request.user.pk:
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(model).pk,
            #content_type_id=ContentType.objects.get_for_model(model).model,
            object_id=object_id,
            object_repr=object_unicode,
            change_message=obtener_ip(request),
            # action flag es 0 listar,1 agregar,2 modificar,3 eliminar,4 entrar, 5 salir, 6 activar, 7 desactivar, 8 reactivar, 9 Error User Password, 10 user login apk, 11 Base de datos
            action_flag=action,
        )
    else:
        LogEntry.objects.log_action(
            user_id=1,
            content_type_id=ContentType.objects.get_for_model(model).pk,
            #content_type_id=ContentType.objects.get_for_model(model).model,
            object_id=object_id,
            object_repr=object_unicode,
            change_message=obtener_ip(request),
            # action flag es 0 listar,1 agregar,2 modificar,3 eliminar,4 entrar, 5 salir, 6 activar, 7 desactivar, 8 reactivar, 9 Error User Password, 10 user login apk, 11 base de datos
            action_flag=action
  
        )