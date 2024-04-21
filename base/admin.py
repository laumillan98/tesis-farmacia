from django.contrib import admin
from .models import CustomUser, TipoFarmacia, TurnoFarmacia, TipoMedicamento, Provincia, Municipio, Medicamento, Farmacia, FarmaUser, FarmaciaMedicamento
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(TipoFarmacia)
admin.site.register(TurnoFarmacia)
admin.site.register(TipoMedicamento)
admin.site.register(Provincia)
admin.site.register(Municipio)
admin.site.register(Medicamento)
admin.site.register(Farmacia)
admin.site.register(FarmaUser)
admin.site.register(FarmaciaMedicamento)
