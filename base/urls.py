from django.urls import path 
from . import views
#from django.contrib.auth import views as auth_views

urlpatterns = [
     path('', views.inicio),
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
     path('lista_de_usuarios/', views.listaDeUsuarios),
     path('registrar_farmaceutico/', views.registrarFarmaceutico),
     path('gestionar_usuarios/eliminarUsuario/<username>/', views.eliminarUsuario, name='eliminar_usuario'),
     path('gestionar_usuarios/activarUsuario/<username>/', views.activarUsuario, name ='activar_usuario'),
     path('gestionar_usuarios/editarUsuario/<username>/', views.editarUsuario, name ='editar_usuario'),
     path('gestionar_farmacias/', views.gestionarFarmacias),
     path('lista_de_farmacias/', views.listaDeFarmacias),
     path('registrar_farmacia/', views.registrarFarmacia),
     path('gestionar_farmacias/eliminarFarmacia/<nombre>/', views.eliminarFarmacia, name='eliminar_farmacia'),
     path('gestionar_farmacias/activarFarmacia/<nombre>/', views.activarFarmacia, name ='activar_farmacia'),
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