$(document).ready(function() {
    let map;
    let marker;
    let userMarker; // Variable para guardar el marcador del usuario
    let routingControl;
    var locationControl;
    let resultadosTabla;

    $('#buscarMedicamentoBtn').click(function() {
        var nombreMedicamento = $('#nombre_medicamento').val();

        $.ajax({
            url: buscarMedicamentoUrl,
            type: "GET",
            data: { nombre_medicamento: nombreMedicamento },
            success: function(response) {
                if(resultadosTabla) {
                    resultadosTabla.clear()
                    resultadosTabla.destroy();
                }

                resultadosTabla = $('#resultadosTabla').DataTable({
                    "columnDefs": [
                        {
                            "targets": 3,
                            "render": function (data, type, row) {
                                let existenciaClass = data.existencia > 10 ? 'existencia-alta' : 'existencia-baja';
                                let existenciaTexto = data.existencia > 10 ? 'Suficientes unidades' : 'Pocas unidades';
                                // Apply a CSS class for special formatting:
                                let button = `<a href="#" id="notificame" class="icon-button" data-medic=`+data.medicamento+`>
                                (Avísame <i class="fa-solid fa-bell"></i>)</a>`
                                if(data.existencia > 10 || data.notificacion_activa) {
                                    button = ''
                                }
                                let texto = '<p class="'+existenciaClass+'">' + existenciaTexto + ' '+button+ '</p>'
                                return texto;
                            }
                        },
                        {
                            "targets": 4, // Index of the actions column
                            "render": function (data, type, row) {
                                let button = "<button class='btn btn-info ver-mapa-btn'"+
                                " data-lat="+row[3].latitude+' data-lng='+row[3].longitude+' data-name='+row[3].nombre+"><i class='fa-solid fa-map-location-dot'></i></button>"
                                return button;
                            }
                        },
                        {
                            "targets": 5, // Index of the actions column
                            "render": function (data, type, row) {
                              let button ="<button class='btn btn-warning ver-reacciones-btn' data-desc='"+data+"'><i class='fa-solid fa-triangle-exclamation' style='color:white'></i></button>"
                              return button;
                            }
                        }
                    ],
                });
                resultadosTabla.clear();

                if (response.result.length > 0) {
                    if (response.has_interactions) {
                        toastr.error('Los resultados de busqueda muetran medicamentos con reacciones, presione sobre el icono ⚠️ para visualizarlas');
                    }    
                    $.each(response.result, function(index, farmacia) {
                        let location = {'nombre': farmacia.nombre_farmacia, 'latitude': farmacia.latitud, 'longitude': farmacia.longitud}
                        let existencia = {'medicamento': farmacia.id_medic,'existencia': farmacia.existencia, 'notificacion_activa': farmacia.notificacion_activa}
                        resultadosTabla.row.add([
                            index + 1,
                            farmacia.medicamento,
                            farmacia.nombre_farmacia,
                            existencia,
                            location,
                            farmacia.reacciones
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
                
                    $('.ver-reacciones-btn').click(function() {
                        let reac = $(this).data('desc');
                
                        $('#reacModal').data('desc', reac);
                        $('#reacModal').modal('show');
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
                         
                        }
                      });
                }
            },
            error: function(response) {
                Swal.fire({
                    title: 'Error',
                    text: 'Debe introducir un medicamento para poder realizar la búsqueda.',
                    icon: 'error',
                    confirmButtonText: 'Aceptar'
                });
            }
        });
    });

    function notificame() {
        $('#notificame').on('click', function(event) {
            event.preventDefault(); // Previene la acción por defecto del enlace
        
            let medic = $(this).data('medic');
            // Realiza la solicitud AJAX
            $.ajax({
                url: '/crear_notificacion/', 
                type: 'GET', 
                data: {
                    'medicamento': medic
                },
                success: function(response) {
                    // Si la respuesta es exitosa, oculta el icono
                    Swal.fire({
                        title: "Good job!",
                        text: "You clicked the button!",
                        icon: "success"
                    });
                    $('#notificame').hide();
                },
                error: function(xhr, status, error) {
                    // Manejo opcional de errores
                    console.error("Error en la solicitud AJAX:", status, error);
                }
            });
        });
    }

    $('#reacModal').on('shown.bs.modal', function() {
        const reac = $('#reacModal').data('desc');
        $('#reacciones-id').text(reac);
    });

   
    $('#mapaModal').on('shown.bs.modal', function() {
        const pharmacyLat = $('#mapaModal').data('lat');
        const pharmacyLng = $('#mapaModal').data('lng');
        const pharmacyName = $('#mapaModal').data('name');

        if (map) {
            map.remove();
        }

        map = L.map('mapa').setView([pharmacyLat, pharmacyLng], 18);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; OpenStreetMap contributors'
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
        L.marker([pharmacyLat, pharmacyLng], {draggable: false}).addTo(map).bindPopup("Farmacia" + pharmacyName).openPopup();
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

});
