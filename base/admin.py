from django.contrib import admin
from .models import CustomUser, TipoFarmacia, TurnoFarmacia, RestriccionMedicamento, ClasificacionMedicamento, FormatoMedicamento, Provincia, Municipio, Medicamento, Farmacia, FarmaUser, FarmaciaMedicamento, Entrada, Salida
from django.contrib.gis.geos import Point
from leaflet.admin import LeafletGeoAdmin
from .forms import FarmaciaAdminForm
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(TipoFarmacia)
admin.site.register(TurnoFarmacia)
admin.site.register(RestriccionMedicamento)
admin.site.register(ClasificacionMedicamento)
admin.site.register(FormatoMedicamento)
admin.site.register(Provincia)
admin.site.register(Municipio)
admin.site.register(FarmaUser)
admin.site.register(FarmaciaMedicamento)
admin.site.register(Medicamento)
admin.site.register(Entrada)
admin.site.register(Salida)


@admin.register(Farmacia)
class FarmaciaAdmin(LeafletGeoAdmin):
    form = FarmaciaAdminForm

    def save_model(self, request, obj, form, change):
        if 'latitud' in form.cleaned_data and 'longitud' in form.cleaned_data:
            latitud = form.cleaned_data['latitud']
            longitud = form.cleaned_data['longitud']
            if latitud is not None and longitud is not None:
                obj.ubicacion = Point(longitud, latitud)
        super(FarmaciaAdmin, self).save_model(request, obj, form, change)


