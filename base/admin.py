from django.contrib import admin
from .models import CustomUser, TipoFarmacia, TurnoFarmacia, RestriccionMedicamento, ClasificacionMedicamento, FormatoMedicamento, Provincia, Municipio, Medicamento, Farmacia, FarmaUser, FarmaciaMedicamento
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


"""@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    form = MedicamentoAdminForm
    list_display = ['nombre', 'cant_max', 'precio_unidad', 'origen_natural']
    search_fields = ['nombre']
    filter_horizontal = ('reacciones',)"""