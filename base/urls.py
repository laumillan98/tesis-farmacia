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
     path('activate/<uidb64>/<token>', views.activate, name='activate'),
     path('registrar/', views.registrar),
     path("cambiarPass", views.cambiarPass, name="cambiarPass"),
     path("solicitar_restablecer_pass", views.restablecerPass, name="solicitar_restablecer_pass"),
     path('reset/<uidb64>/<token>', views.confirmarRestablecerPass, name='cambiar_pass'),
     # Usuarios
     path('perfil_de_usuario/<username>/', views.perfilUsuario, name='perfil_de_usuario'),
     path('gestionar_usuarios/', views.gestionarUsuarios),
     path('lista_de_usuarios/', views.listaDeUsuarios, name='lista_de_usuarios'),
     path('registrar_farmaceutico/', views.registrarFarmaceutico,  name='registrar_farmaceutico'),
     path('registrar_especialista/', views.registrarEspecialista,  name='registrar_especialista'),
     path('registrar_administrador/', views.registrarAdministrador,  name='registrar_administrador'),
     path('gestionar_usuarios/eliminarUsuario/<username>/', views.eliminarUsuario, name='eliminar_usuario'),
     path('gestionar_usuarios/activarUsuario/<username>/', views.activarUsuario, name ='activar_usuario'),
     path('gestionar_usuarios/obtenerUsuario/<username>/', views.obtenerUsuario, name ='obtener_usuario'),
     path('gestionar_usuarios/editarUsuario/', views.editarUsuario, name ='editar_usuario'),
     # Provincias
     path('gestionar_provincias/', views.gestionarProvincias),
     path('lista_de_provincias/', views.listaDeProvincias, name='lista_de_provincias'),
     path('gestionar_provincias/registrarProvincia/', views.registrarProvincia, name='registrar_provincia'),
     path('gestionar_provincias/obtenerProvincia/<uuid>/', views.obtenerProvincia, name ='obtener_provincia'),
     path('gestionar_provincias/editarProvincia/', views.editarProvincia, name ='editar_provincia'),
     # Municipios
     path('gestionar_municipios/', views.gestionarMunicipios),
     path('lista_de_municipios/', views.listaDeMunicipios, name='lista_de_municipios'),
     path('gestionar_municipios/registrarMunicipio/', views.registrarMunicipio, name='registrar_municipio'),
     path('gestionar_municipios/obtenerProvMunicipio/', views.obtenerProvMunicipio, name ='obtener_provmunicipio'),
     path('gestionar_municipios/obtenerMunicipio/<uuid>/', views.obtenerMunicipio, name ='obtener_municipio'),
     path('gestionar_municipios/editarMunicipio/', views.editarMunicipio, name ='editar_municipio'),
     #Farmacias
     path('gestionar_farmacias/', views.gestionarFarmacias),
     path('lista_de_farmacias/', views.listaDeFarmacias, name='lista_de_farmacias'),
     path('registrar_farmacia/', views.registrarFarmacia),
     path('gestionar_farmacias/obtenerFarmacia/<uuid>/', views.obtenerFarmacia, name ='obtener_farmacia'),
     path('gestionar_farmacias/editarFarmacia/', views.editarFarmacia, name ='editar_farmacia'),
          # Tipo Farmacia
     path('gestionar_tipos_de_farmacias/', views.gestionarTiposFarmacias),
     path('lista_tipos_de_farmacias/', views.listaDeTiposDeFarmacias, name='lista_tipos_de_farmacias'),
     path('gestionar_tipos_de_farmacias/registrarTipoFarmacia/', views.registrarTipoFarmacia, name='registrar_tipo_de_farmacia'),
     path('gestionar_tipos_de_farmacias/obtenerTipoFarmacia/<uuid>/', views.obtenerTipoFarmacia, name ='obtener_tipo_de_farmacia'),
     path('gestionar_tipos_de_farmacias/editarTipoFarmacia/', views.editarTipoFarmacia, name ='editar_tipo_de_farmacia'),
          #Turno Farmacia
     path('gestionar_turnos_de_farmacias/', views.gestionarTurnosFarmacias),
     path('lista_turnos_de_farmacias/', views.listaDeTurnosDeFarmacias, name='lista_turnos_de_farmacias'),
     path('gestionar_turnos_de_farmacias/registrarTurnoFarmacia/', views.registrarTurnoFarmacia, name='registrar_turno_de_farmacia'),
     path('gestionar_turnos_de_farmacias/obtenerTurnoFarmacia/<uuid>/', views.obtenerTurnoFarmacia, name ='obtener_turno_de_farmacia'),
     path('gestionar_turnos_de_farmacias/editarTurnoFarmacia/', views.editarTurnoFarmacia, name ='editar_turno_de_farmacia'),
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
     path('gestionar_restricciones_de_medicamentos/registrarRestriccionMedicamento/', views.registrarRestriccionMedicamento, name='registrar_restriccion_de_medicamento'),
     path('gestionar_restricciones_de_medicamentos/obtenerRestriccionMedicamento/<uuid>/', views.obtenerRestriccionMedicamento, name ='obtener_restriccion_de_medicamento'),
     path('gestionar_restricciones_de_medicamentos/editarRestriccionMedicamento/', views.editarRestriccionMedicamento, name ='editar_restriccion_de_medicamento'),
          # Clasificacion Medicamento
     path('gestionar_clasificaciones_de_medicamentos/', views.gestionarClasificacionesMedicamentos),
     path('lista_clasificaciones_de_medicamentos/', views.listaDeClasificacionesDeMedicamentos, name='lista_clasificaciones_de_medicamentos'),
     path('gestionar_clasificaciones_de_medicamentos/registrarClasificacionMedicamento/', views.registrarClasificacionMedicamento, name='registrar_clasificacion_de_medicamento'),
     path('gestionar_clasificaciones_de_medicamentos/obtenerClasificacionMedicamento/<uuid>/', views.obtenerClasificacionMedicamento, name ='obtener_clasificacion_de_medicamento'),
     path('gestionar_clasificaciones_de_medicamentos/editarClasificacionMedicamento/', views.editarClasificacionMedicamento, name ='editar_clasificacion_de_medicamento'),
          # Formato Medicamento
     path('gestionar_formatos_de_medicamentos/', views.gestionarFormatosMedicamentos),
     path('lista_formatos_de_medicamentos/', views.listaDeFormatosDeMedicamentos, name='lista_formatos_de_medicamentos'),
     path('gestionar_formatos_de_medicamentos/registrarFormatoMedicamento/', views.registrarFormatoMedicamento, name='registrar_formato_de_medicamento'),
     path('gestionar_formatos_de_medicamentos/obtenerFormatoMedicamento/<uuid>/', views.obtenerFormatoMedicamento, name ='obtener_formato_de_medicamento'),
     path('gestionar_formatos_de_medicamentos/editarFormatoMedicamento/', views.editarFormatoMedicamento, name ='editar_formato_de_medicamento'),
     # Farmacia Medicamento
     path('gestionar_medicfarma/', views.gestionarMedicFarma),
     path('lista_de_medicfarma/', views.listaDeMedicFarma, name='lista_de_medicfarma'),
     path('gestionar_medicfarma/obtenerDescripcion/<uuid>/', views.obtenerDescripcion, name ='obtener_descripcion'),
     #path('actualizar_fecha_expiracion/', views.actualizarFechaExpiracion, name='actualizar_fecha_expiracion'),
     path('actualizar_existencia/', views.actualizarExistencia, name='actualizar_existencia'),
     path('gestionar_medicamentos_disponibles/', views.gestionarMedicamentosDisponibles, name = 'gestionar_medicamentos_disponibles'),
     path('lista_de_medicamentos_disponibles/', views.listaDeMedicamentosDisponibles, name='lista_de_medicamentos_disponibles'),
     path('gestionar_medicamentos_disponibles/obtenerDescripcion/<uuid>/', views.obtenerDescripcion, name ='obtener_descripcion'),
     path('gestionar_medicamentos_disponibles/exportarMedicamento/<uuid>/', views.exportarMedicamento, name='exportar_medicamento'),
          #Entradas
     path('gestionar_entradas_medicamento/', views.gestionarEntradasMedicamento),
     path('lista_de_entradas_medicamento/', views.listaDeEntradasMedicamento, name='lista_de_entradas_medicamento'),
     path('gestionar_entradas_medicamento/obtenerEntradaMedicamento/<uuid>/', views.obtenerEntradaMedicamento, name ='obtener_entrada_de_medicamento'),
     path('gestionar_entradas_medicamento/editarEntradaMedicamento/', views.editarEntradaMedicamento, name ='editar_entrada_de_medicamento'),
          #Salidas
     path('gestionar_salidas_medicamento/', views.gestionarSalidasMedicamento),
     path('lista_de_salidas_medicamento/', views.listaDeSalidasMedicamento, name='lista_de_salidas_medicamento'),

     # Cliente
     # Buscar Informacion de Medicamentos
     path('visualizar_tabla_medicamentos/', views.visualizarTablaMedicamentos),
     path('buscar_infoMedicamento/', views.buscarInfoMedicamento, name='buscar_infoMedicamento'),
      path('visualizar_tabla_medicamentos/obtenerDescripcion/<uuid>/', views.obtenerDescripcion, name ='obtener_descripcion'),
     # Buscar Existencias de Medicamentos 
     path('buscar_medicamento/', views.buscarMedicamento, name='buscar_medicamento'),
     # Buscar Farmacias por Municipio
     path('visualizar_tabla_farmacias/', views.visualizarTablaFarmacias),
     path('buscar_farmacia/', views.buscarFarmacia, name='buscar_farmacia'),
     # Trazas
     path('visualizar_trazas_crud/', views.visualizarTrazasCrud),
     path('lista_de_trazas_crud/', views.listaDeTrazasCrud, name='lista_de_trazas_crud'),
     path('visualizar_trazas_sistema/', views.visualizarTrazasSistema),
     path('lista_de_trazas_sistema/', views.listaDeTrazasSistema, name='lista_de_trazas_sistema'),
     # Reportes PDF
     path('generar_reporte_pdf/', views.generar_reporte_pdf, name='generar_reporte_pdf'),
     # Alertas
     path('crear_notificacion/', views.crearTareaNotificacion, name='crear_notificacion'),
     # Graficos
     path('visualizar_charts/', views.visualizarCharts),
     path('usuarios_xgrupos_chart/', views.usuariosXGruposChart, name='usuarios_xgrupos_chart'),
]

