$.getScript("/static/js/datatables.spanish.js", function() {      
   $(document).ready(function() {
        let map;
        let userMarker; // Variable para guardar el marcador del usuario
        let routingControl;
        var locationControl;
        let tablaMedicamento;
        let tablaDisponibilidad;
        $('#disponibilidadTabla').hide();

        $('#buscarMedicamentoBtn').click(function() {
            var nombreMedicamento = $('#nombre_medicamento').val();

            $.ajax({
                url: '/buscar_infoMedicamento/',
                type: "GET",
                data: { nombre_medicamento: nombreMedicamento },
                success: function(response) {
                    if(tablaDisponibilidad) {
                        $('#disponibilidadTabla').hide();
                    }

                    if(tablaMedicamento) {
                        tablaMedicamento.clear();
                        tablaMedicamento.destroy();
                    }

                    tablaMedicamento = $('#resultadosTabla').DataTable({
                        "columnDefs": [
                            {
                                "targets": 8, // Index of the actions column
                                "render": function (data, type, row) {
                                let buttonDesc ="<button class='btn btn-sm btn-info mostrar-descripcion-btn mr-2' data-desc='"+data.desc+"' "+ 
                                "data-toggle='modal' data-target='#modaldesc-lg'><i class='fa-solid fa-eye'></i></button>"
                                let buttonReac ="<button class='btn btn-sm btn-warning ver-reacciones-btn' data-desc='"+data.reac+"'><i class='fa-solid fa-triangle-exclamation' style='color:white'></i></button>"
                                return buttonDesc + buttonReac;
                                }
                            },
                            {
                                "targets": -1, // Index of the actions column
                                "render": function (data, type, row) {
                                let button ="<button class='btn btn-sm btn-info mostrar-disponibilidad' data-id="+data+"><i class='fa-solid fa-magnifying-glass-location'></i></button>"
                                return button;
                                }
                            }
                        ]
                    });

                    if (response.result.length > 0) {
                        if (response.has_interactions) {
                            toastr.error('Los resultados de búsqueda muestran medicamentos con reacciones, presione sobre el ícono ⚠️ para visualizarlas');
                        }    
                        $.each(response.result, function(index, medicamento) {
                            tablaMedicamento.row.add([
                                index + 1,
                                medicamento.nombre,
                                medicamento.formato,
                                medicamento.cant_max,
                                medicamento.precio_unidad,
                                medicamento.origen,
                                medicamento.restriccion,
                                medicamento.clasificacion,
                                {'desc': medicamento.description, 'reac': medicamento.reacciones},
                                medicamento.id
                            ]).draw();
                        });

                        $('.mostrar-descripcion-btn').click(function() {
                            let desc = $(this).data('desc');
                            cargarDescripcionMedicamento(desc);
                        });

                        $('.mostrar-disponibilidad').click(function() {
                            let id = $(this).data('id');
                            cargarDisponibilidad(id);
                        });

                        $('.ver-reacciones-btn').click(function() {
                            let desc = $(this).data('desc');
                            $('#reacciones-id').html(desc);
                            $('#reacModal').modal('show');
                        });

                    } else {
                        Swal.fire({
                            title: 'No encontrado',
                            text: 'No se encontraron medicamentos con el nombre buscado.',
                            icon: 'info',
                            confirmButtonText: 'Aceptar'
                        });
                    }
                },
                error: function(response) {
                    Swal.fire({
                        title: 'Error',
                        text: 'Debe introducir un nombre de medicamento para poder realizar la búsqueda.',
                        icon: 'error',
                        confirmButtonText: 'Aceptar'
                    });
                }
            });
        });
    
        function cargarDescripcionMedicamento(desc) {
            $('#descripcionMostrar').html(desc);
            $('#modaldesc-lg').modal('show'); 
        }

        function cargarDisponibilidad(id) {
            $.ajax({
                url: '/buscar_medicamento/',
                type: "GET",
                data: { id_medicamento: id },
                success: function(response) {
                    if(response.result.length > 0) {
                        $('#disponibilidadTabla').show();

                        if(tablaDisponibilidad) {
                            tablaDisponibilidad.clear()
                            tablaDisponibilidad.destroy();
                        }
                        tablaDisponibilidad = $('#disponibilidadTabla').DataTable({
                            "columnDefs": [
                                {
                                    "targets": 6,
                                    "render": function (data, type, row) {
                                        let existenciaClass = data > 10 ? 'existencia-alta' : 'existencia-baja';
                                        let existenciaTexto = data > 10 ? 'Suficientes unidades' : 'Pocas unidades';
                                        // Apply a CSS class for special formatting:
                                        let texto = '<p class="'+existenciaClass+'">' + existenciaTexto + '</p>'
                                        return texto;
                                    }
                                },
                                {
                                    "targets": 7, // Index of the actions column
                                    "render": function (data, type, row) {
                                        let button = "<button class='btn btn-info ver-mapa-btn'"+
                                        " data-lat='"+row[7].latitude+"' data-lng='"+row[7].longitude+"' data-name='"+row[7].nombre+"'><i class='fa-solid fa-map-location-dot'></i></button>";
                                        return button;
                                    }
                                },
                            ],
                        });

                        $.each(response.result, function(index, farmacia) {
                            let location = {'nombre': farmacia.nombre_farmacia, 'latitude': farmacia.latitud, 'longitude': farmacia.longitud}
                            tablaDisponibilidad.row.add([
                                index + 1,
                                farmacia.nombre_farmacia,
                                farmacia.nombre_municipio,
                                farmacia.direccion,
                                farmacia.telefono,
                                farmacia.turno,
                                farmacia.existencia,
                                location,
                            ]).draw();
                        });

                        $('.ver-mapa-btn').click(function() {
                            var lat = $(this).data('lat');
                            var lng = $(this).data('lng');
                            var name = $(this).data('name');
                    
                            $('#mapaModal').data('lat', lat);
                            $('#mapaModal').data('lng', lng);
                            $('#mapaModal').data('name', name);
                            $('#mapaModal').modal('show');
                        });
                    } else {
                        Swal.fire({
                            title: 'No encontrado',
                            text: 'No se encontraron farmacias con el medicamento buscado.',
                            icon: 'info',
                            showCancelButton: true,
                            confirmButtonText: 'Avísame 🔔',
                            cancelButtonText: 'Cerrar'
                        }).then((result) => {
                            if (result.isConfirmed) {
                                notificame(id);
                            }
                        });
                    }
                },
                error: function(error) {
                    console.log(error);
                }
            });
        }

        $('#mapaModal').on('shown.bs.modal', function() {
            const pharmacyLat = $('#mapaModal').data('lat');
            const pharmacyLng = $('#mapaModal').data('lng');
            const pharmacyName = $('#mapaModal').data('name');
            console.log(pharmacyLat);
            console.log(pharmacyLng);

            if (map) {
                map.remove();
            }

            map = L.map('mapa').setView([pharmacyLat, pharmacyLng], 18);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '&copy; OpenStreetMap contributors'
            }).on('tileerror', function(error, tile){
                console.error("error al cargar", error, tile);
            }).addTo(map);
            locationControl = L.control.locate({
                position: 'topleft',
                setView: 'once', // Mover el mapa a la ubicación obtenida una vez
                keepCurrentZoomLevel: true,
                showPopup: true,
                strings: {
                    title: "Show me where I am"
                },
                locateOptions: {
                    maxZoom: 16,
                    watch: true, // Seguir observando
                    setView: false // No ajustar la vista
                }
            }).addTo(map);
            L.marker([pharmacyLat, pharmacyLng], {draggable: false}).addTo(map).bindPopup("Farmacia " + pharmacyName).openPopup();
            // Agregar un callback para cuando se encuentra la ubicación del usuario
            map.on('locationfound', function(e) {
                const userLatLng = e.latlng;

                if (userMarker) {
                    map.removeLayer(userMarker);
                }

                clearRouteAndHideDirections();

                // Añadir marcador y círculo en la ubicación del usuario
                userMarker = L.marker(userLatLng, {draggable: true}).addTo(map)
                    .bindPopup('Mi Ubicación')
                    .openPopup();

                userMarker.on('dragend', (event) => {
                    console.error("DRAGGED");
                    const marker = event.target;
                    const newPosition = marker.getLatLng();
                    $('#routeIcon').data('userLocation', newPosition);
                    // Update the route with the new position of the marker
                    //updateRouting(newPosition, pharmacyLat, pharmacyLng);
                });

                map.setView(userLatLng, map.getZoom());
                locationControl.stop();
                $('#routeIcon').data('userLocation', userLatLng);
                $('#routeIcon').css('display', 'flex');
                // Trazar la ruta desde la ubicación del usuario hasta la tienda
                //updateRouting(userLatLng, pharmacyLat, pharmacyLng);
            });

            map.on('locationerror', (e) => {
                alert(e.message);
            });

        });


        $('#routeIcon').click(function() {
            const userLocation = $(this).data('userLocation');
            const pharmacyLat = $('#mapaModal').data('lat');
            const pharmacyLng = $('#mapaModal').data('lng');
            updateRouting(userLocation, pharmacyLat, pharmacyLng)
        });


        function clearRouteAndHideDirections() {
            if(routingControl != null) {
                map.removeControl(routingControl);
            }
        }


        function updateRouting(userLatLng, pharmacyLat, pharmacyLng) {
            if (routingControl) {
                map.removeControl(routingControl);
            }
            routingControl = L.Routing.control({
                waypoints: [
                    userLatLng,
                    L.latLng(pharmacyLat, pharmacyLng)
                ],
                createMarker: function(i, waypoint, n) {
                    // Personalizar los marcadores de inicio y fin
                    if (i === n - 1) {
                        // Make the destination marker non-draggable
                        return L.marker(waypoint.latLng, {
                            draggable: false,
                        });
                    } else {
                        // Other markers can be draggable
                        return userMarker;
                    }
                },
                routeWhileDragging: false,
                addWaypoints: false
            }).addTo(map);
        }


        $('#mapaModal').on('hidden.bs.modal', function() {
            $('#routeIcon').css('display', 'none');
        });

        // Funcion para notificar cuando haya un medicamento en existencia
        function notificame(id_medic) {
            $.ajax({
                url: '/crear_notificacion/', 
                type: 'GET', 
                data: {
                    'medicamento': id_medic
                },
                success: function(response) {
                    // Si la respuesta es exitosa, oculta el icono
                    Swal.fire({
                        title: "Listo!",
                        text: "Hemos creado tu alerta con éxito, será avisado pronto",
                        icon: "success"
                    });
                },
                error: function(xhr, status, error) {
                    // Manejo opcional de errores
                    console.error("Error en la solicitud AJAX:", status, error);
                }
            });
        }
    });
});