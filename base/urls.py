from django.urls import path 
from . import views
#from django.contrib.auth import views as auth_views

urlpatterns = [
     path('', views.inicio),
     path('administrator/', views.administrator, name = "index"),
     path('aviso_login_requerido/', views.avisoLoginRequerido),
     path('salir/', views.salir),
     path('acceder/', views.autenticar, name='acceder'),
     path('activate/<uidb64>/<token>', views.activate, name='activate'),
     path('registrar/', views.registrar),
     path("cambiarPass", views.cambiarPass, name="cambiarPass"),
     path("solicitar_restablecer_pass", views.restablecerPass, name="solicitar_restablecer_pass"),
     path('reset/<uidb64>/<token>', views.confirmarRestablecerPass, name='cambiar_pass'),
     path('perfil_de_usuario/<username>/', views.perfilUsuario, name='perfil_de_usuario'),
     path('gestionar_usuarios/', views.gestionarUsuarios),
     path('lista_de_usuarios/', views.listaDeUsuarios, name='lista_de_usuarios'),
     path('registrar_farmaceutico/', views.registrarFarmaceutico),
     path('gestionar_usuarios/eliminarUsuario/<username>/', views.eliminarUsuario, name='eliminar_usuario'),
     path('gestionar_usuarios/activarUsuario/<username>/', views.activarUsuario, name ='activar_usuario'),
     path('gestionar_usuarios/editarUsuario/', views.editarUsuario, name ='editar_usuario'),
     path('gestionar_usuarios/obtenerUsuario/<username>/', views.obtenerUserPorUsername, name ='obtener_usuario'),
     path('gestionar_farmacias/', views.gestionarFarmacias),
     path('lista_de_farmacias/', views.listaDeFarmacias, name='lista_de_farmacias'),
     path('registrar_farmacia/', views.registrarFarmacia),
     path('gestionar_farmacias/eliminarFarmacia/<uuid>/', views.eliminarFarmacia, name='eliminar_farmacia'),
     path('gestionar_farmacias/activarFarmacia/<uuid>/', views.activarFarmacia, name ='activar_farmacia'),
     path('gestionar_farmacias/editarFarmacia/<uuid>/', views.editarFarmacia, name ='editar_farmacia'),
     path('gestionar_municipios/', views.gestionarMunicipios),
     path('lista_de_municipios/', views.listaDeMunicipios),
     path('registrar_municipio/', views.registrarMunicipio),
     path('gestionar_provincias/eliminarProvincia/<uuid>/', views.eliminarProvincia, name='eliminar_provincia'),
     path('gestionar_provincias/activarProvincia/<uuid>/', views.activarProvincia, name ='activar_provincia'),
     path('gestionar_provincias/editarProvincia/<uuid>/', views.editarProvincia, name ='editar_provincia'),
     path('gestionar_provincias/', views.gestionarProvincias),
     path('lista_de_provincias/', views.listaDeProvincias),
     path('registrar_provincia/', views.registrarProvincia),
     path('gestionar_municipios/eliminarMunicipio/<uuid>/', views.eliminarMunicipio, name='eliminar_municipio'),
     path('gestionar_municipios/activarMunicipio/<uuid>/', views.activarMunicipio, name ='activar_municipio'),
     path('gestionar_municipios/editarMunicipio/<uuid>/', views.editarMunicipio, name ='editar_municipio'),
     path('gestionar/', views.gestionarMedicamentos),
     path('registrarMedicamento/', views.registrarMedicamento),
     path('gestionar/editarMedicamento/<uuid>', views.editarMedicamento),
     path('edicionMedicamento/', views.edicionMedicamento),
     path('gestionar/eliminarMedicamento/<uuid>', views.eliminarMedicamento),
     path('actualizarCantidad', views.actualizarCantidad),
     path('farmacias_tabla/', views.farmaciasTabla),
     path('medicamentos_tabla/', views.medicamentosTabla),
     path('existencias_tabla/', views.existenciasTabla),
     path('buscarMedicamento/', views.buscarMedicamento),
     path('buscarDisponibilidad/', views.buscarDisponibilidad),
     path('buscarMunicipio/', views.buscarMunicipio),
     path('buscarDisponibilidadFarmacia/', views.buscarDisponibilidadFarmacia),
     path('buscarDescripcionMedicamento/', views.buscarDescripcionMedicamento),
]