from django.urls import path 
from . import views
#from django.contrib.auth import views as auth_views

urlpatterns = [
     path('', views.inicio),
     path('administrator/', views.administrator, name = "index"),
     path('farmaceutico/', views.farmaceutico, name = "index_farmaceutico"),
     path('backup_database/', views.backup_database, name='backup_database'),
     path('restore_database/', views.restore_database, name='restore_database'),
     path('salir/', views.salir),
     path('acceder/', views.autenticar, name='acceder'),
     path('activate/<username>/<token>', views.activate, name='activate'),
     path('registrar/', views.registrar),
     path("cambiarPass", views.cambiarPass, name="cambiarPass"),
     path("solicitar_restablecer_pass", views.restablecerPass, name="solicitar_restablecer_pass"),
     path('reset/<uidb64>/<token>', views.confirmarRestablecerPass, name='cambiar_pass'),
     # Usuarios
     path('perfil_de_usuario/<username>/', views.perfilUsuario, name='perfil_de_usuario'),
     path('gestionar_usuarios/', views.gestionarUsuarios),
     path('lista_de_usuarios/', views.listaDeUsuarios, name='lista_de_usuarios'),
     path('registrar_farmaceutico/', views.registrarFarmaceutico,  name='registrar_farmaceutico'),
     path('gestionar_usuarios/eliminarUsuario/<username>/', views.eliminarUsuario, name='eliminar_usuario'),
     path('gestionar_usuarios/activarUsuario/<username>/', views.activarUsuario, name ='activar_usuario'),
     path('gestionar_usuarios/obtenerUsuario/<username>/', views.obtenerUsuario, name ='obtener_usuario'),
     path('gestionar_usuarios/editarUsuario/', views.editarUsuario, name ='editar_usuario'),
     #Farmacias
     path('gestionar_farmacias/', views.gestionarFarmacias),
     path('lista_de_farmacias/', views.listaDeFarmacias, name='lista_de_farmacias'),
     path('registrar_farmacia/', views.registrarFarmacia),
     path('gestionar_farmacias/obtenerFarmacia/<uuid>/', views.obtenerFarmacia, name ='obtener_farmacia'),
     path('gestionar_farmacias/editarFarmacia/', views.editarFarmacia, name ='editar_farmacia'),
          # Tipo Farmacia
     path('gestionar_tipos_de_farmacias/', views.gestionarTiposFarmacias),
     path('lista_tipos_de_farmacias/', views.listaDeTiposDeFarmacias, name='lista_tipos_de_farmacias'),
     path('registrar_tipo_de_farmacia/', views.registrarTipoFarmacia),
     path('gestionar_tipos_de_farmacias/obtenerTipoFarmacia/<uuid>/', views.obtenerTipoFarmacia, name ='obtener_tipo_de_farmacia'),
     path('gestionar_tipos_de_farmacias/editarTipoFarmacia/', views.editarTipoFarmacia, name ='editar_tipo_de_farmacia'),
          #Tuno Farmacia
     path('gestionar_turnos_de_farmacias/', views.gestionarTurnosFarmacias),
     path('lista_turnos_de_farmacias/', views.listaDeTurnosDeFarmacias, name='lista_turnos_de_farmacias'),
     path('registrar_turno_de_farmacia/', views.registrarTurnoFarmacia),
     path('gestionar_turnos_de_farmacias/obtenerTurnoFarmacia/<uuid>/', views.obtenerTurnoFarmacia, name ='obtener_turno_de_farmacia'),
     path('gestionar_turnos_de_farmacias/editarTurnoFarmacia/', views.editarTurnoFarmacia, name ='editar_turno_de_farmacia'),
     # Municipios
     path('gestionar_municipios/', views.gestionarMunicipios),
     path('lista_de_municipios/', views.listaDeMunicipios, name='lista_de_municipios'),
     path('registrar_municipio/', views.registrarMunicipio),
     path('gestionar_municipios/obtenerMunicipio/<uuid>/', views.obtenerMunicipio, name ='obtener_municipio'),
     path('gestionar_municipios/editarMunicipio/', views.editarMunicipio, name ='editar_municipio'),
     # Provincias
     path('gestionar_provincias/', views.gestionarProvincias),
     path('lista_de_provincias/', views.listaDeProvincias, name='lista_de_provincias'),
     path('registrar_provincia/', views.registrarProvincia),
     path('gestionar_provincias/obtenerProvincia/<uuid>/', views.obtenerProvincia, name ='obtener_provincia'),
     path('gestionar_provincias/editarProvincia/', views.editarProvincia, name ='editar_provincia'),
     # Farmacia Medicamento
     path('gestionar_medicfarma/', views.gestionarMedicFarma),
     path('lista_de_medicfarma/', views.listaDeMedicFarma, name='lista_de_medicfarma'),
     path('gestionar_medicfarma/obtenerDescripcion/<uuid>/', views.obtenerDescripcion, name ='obtener_descripcion'),
     path('actualizar_existencia/', views.actualizarExistencia, name='actualizar_existencia'),
     path('gestionar_medicamentos_disponibles/', views.gestionarMedicamentosDisponibles, name = 'gestionar_medicamentos_disponibles'),
     path('lista_de_medicamentos_disponibles/', views.listaDeMedicamentosDisponibles, name='lista_de_medicamentos_disponibles'),
     path('gestionar_medicamentos_disponibles/obtenerDescripcion/<uuid>/', views.obtenerDescripcion, name ='obtener_descripcion'),
     path('gestionar_medicamentos_disponibles/exportarMedicamento/<uuid>/', views.exportarMedicamento, name='exportar_medicamento'),
     
     
     
     #Medicamentos
     path('gestionar_medicamentos/', views.gestionarMedicamentos),
     path('lista_de_medicamentos/', views.listaDeMedicamentos, name='lista_de_medicamentos'),
     path('registrar_medicamento/', views.registrarMedicamento),
     path('gestionar_medicamentos/obtenerDescripcion/<uuid>/', views.obtenerDescripcion, name ='obtener_descripcion'),
     path('gestionar_medicamentos/obtenerMedicamento/<uuid>/', views.obtenerMedicamento, name ='obtener_medicamento'),
     path('gestionar_medicamentos/editarMedicamento/', views.editarMedicamento, name ='editar_medicamento'),
          # Restriccion Medicamento
     path('gestionar_restricciones_de_medicamentos/', views.gestionarRestriccionesMedicamentos),
     path('lista_restricciones_de_medicamentos/', views.listaDeRestriccionesDeMedicamentos, name='lista_restricciones_de_medicamentos'),
     path('registrar_restriccion_de_medicamento/', views.registrarRestriccionMedicamento),
     path('gestionar_restricciones_de_medicamentos/obtenerRestriccionMedicamento/<uuid>/', views.obtenerRestriccionMedicamento, name ='obtener_restriccion_de_medicamento'),
     path('gestionar_restricciones_de_medicamentos/editarRestriccionMedicamento/', views.editarRestriccionMedicamento, name ='editar_restriccion_de_medicamento'),
          # Clasificacion Medicamento
     path('gestionar_clasificaciones_de_medicamentos/', views.gestionarClasificacionesMedicamentos),
     path('lista_clasificaciones_de_medicamentos/', views.listaDeClasificacionesDeMedicamentos, name='lista_clasificaciones_de_medicamentos'),
     path('registrar_clasificacion_de_medicamento/', views.registrarClasificacionMedicamento),
     path('gestionar_clasificaciones_de_medicamentos/obtenerClasificacionMedicamento/<uuid>/', views.obtenerClasificacionMedicamento, name ='obtener_clasificacion_de_medicamento'),
     path('gestionar_clasificaciones_de_medicamentos/editarClasificacionMedicamento/', views.editarClasificacionMedicamento, name ='editar_clasificacion_de_medicamento'),
          # Formato Medicamento
     path('gestionar_formatos_de_medicamentos/', views.gestionarFormatosMedicamentos),
     path('lista_formatos_de_medicamentos/', views.listaDeFormatosDeMedicamentos, name='lista_formatos_de_medicamentos'),
     path('registrar_formato_de_medicamento/', views.registrarFormatoMedicamento),
     path('gestionar_formatos_de_medicamentos/obtenerFormatoMedicamento/<uuid>/', views.obtenerFormatoMedicamento, name ='obtener_formato_de_medicamento'),
     path('gestionar_formatos_de_medicamentos/editarFormatoMedicamento/', views.editarFormatoMedicamento, name ='editar_formato_de_medicamento'),
     # Buscar Medicamento
     path('visualizar_existencias_medicamentos/', views.visualizarExistenciasMedicamentos),
     path('buscar_medicamento/', views.buscarMedicamento, name='buscar_medicamento'),

     
     #path('actualizarCantidad', views.actualizarCantidad),
     path('farmacias_tabla/', views.farmaciasTabla),
     path('medicamentos_tabla/', views.medicamentosTabla),
     #path('existencias_tabla/', views.existenciasTabla),
     #path('buscarMedicamento/', views.buscarMedicamento),
     #path('buscarDisponibilidad/', views.buscarDisponibilidad),
     path('buscarMunicipio/', views.buscarMunicipio),
     path('buscarDisponibilidadFarmacia/', views.buscarDisponibilidadFarmacia),
     path('buscarDescripcionMedicamento/', views.buscarDescripcionMedicamento),

     # Trazas
     path('visualizar_trazas/', views.visualizarTrazas),
     path('lista_de_trazas/', views.listaDeTrazas, name='lista_de_trazas'),
     # Graficos
     path('visualizar_charts/', views.visualizarCharts),
     path('usuarios_xgrupos_chart/', views.usuariosXGruposChart, name='usuarios_xgrupos_chart'),
    
     # Reportes
     path('generar_reporte/', views.generar_reporte_pdf, name='generar_reporte_pdf'),
     path('lote_farmacias/', views.generar_lote_farmacias, name='generar_lote_farmacias'),
     path('borrar_lote_farmacias/', views.borrar_lote_farmacias, name='borrar_lote_farmacias'),
]