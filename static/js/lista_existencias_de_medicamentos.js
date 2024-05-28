$(document).ready(function() {
    let map;
    let userMarker; // Variable para guardar el marcador del usuario
    let routingControl;
    var locationControl;
    const apiKey = 'YOUR_API_KEY'; // Reemplaza con tu clave API de OpenRouteService

    $('#buscarMedicamentoBtn').click(function() {
        var nombreMedicamento = $('#nombre_medicamento').val();

        $.ajax({
            url: buscarMedicamentoUrl,
            type: "GET",
            data: { nombre_medicamento: nombreMedicamento },
            success: function(response) {
                var resultadosTabla = $('#resultadosTabla tbody');
                resultadosTabla.empty();

                if (response.length > 0) {
                    $.each(response, function(index, farmacia) {
                        var existenciaClass = farmacia.existencia > 10 ? 'existencia-alta' : 'existencia-baja';
                        var existenciaTexto = farmacia.existencia > 10 ? 'Suficientes unidades' : 'Pocas unidades';
                        var mapaBtnId = 'mapaBtn' + index;

                        resultadosTabla.append(`
                            <tr>
                                <td>${index + 1}</td>
                                <td>${farmacia.nombre_farmacia}</td>
                                <td>${farmacia.direccion}</td>
                                <td>${farmacia.telefono}</td>
                                <td>${farmacia.nombre_provincia}</td>
                                <td>${farmacia.nombre_municipio}</td>
                                <td>${farmacia.tipo}</td>
                                <td>${farmacia.turno}</td>
                                <td class="${existenciaClass}">${existenciaTexto}</td>
                                <td>
                                    <button id="${mapaBtnId}" class="btn btn-info ver-mapa-btn" data-lat="${farmacia.latitud}" data-lng="${farmacia.longitud}" data-name="${farmacia.nombre_farmacia}">
                                        <i class="fa-solid fa-map-location-dot"></i>
                                    </button>
                                </td>
                            </tr>
                        `);
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
                        confirmButtonText: 'Aceptar'
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
        L.marker([pharmacyLat, pharmacyLng], {draggable: false}).addTo(map).bindPopup(pharmacyName).openPopup();
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

   $('#mapaModal').on('hidden.bs.modal', function() {
        $('#routeIcon').css('display', 'none');
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

    function getUserLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(showPosition, showError);
        } else {
            alert("La geolocalización no es soportada por este navegador.");
        }
    }

    function showPosition(position) {
        const userLat = position.coords.latitude;
        const userLng = position.coords.longitude;
        getRoute(userLat, userLng);
    }

    function showError(error) {
        alert(`Error al obtener la ubicación: ${error.message}`);
    }

    function getRoute(userLat, userLng) {
        const pharmacyLat = $('#mapaModal').data('lat');
        const pharmacyLng = $('#mapaModal').data('lng');
        const pharmacyName = $('#mapaModal').data('name');

        const url = `https://api.openrouteservice.org/v2/directions/driving-car?api_key=${apiKey}&start=${userLng},${userLat}&end=${pharmacyLng},${pharmacyLat}`;

        $.ajax({
            url: url,
            method: 'GET',
            success: function(response) {
                const coordinates = response.routes[0].geometry.coordinates;
                const route = coordinates.map(coord => [coord[1], coord[0]]);

                L.marker([userLat, userLng]).addTo(map).bindPopup('Tu ubicación').openPopup();
                L.marker([pharmacyLat, pharmacyLng]).addTo(map).bindPopup(pharmacyName).openPopup();
                L.polyline(route, { color: 'blue' }).addTo(map);
            },
            error: function(error) {
                console.error('Error al obtener la ruta:', error);
                Swal.fire({
                    title: 'Error',
                    text: 'No se pudo encontrar una ruta. Verifica que las coordenadas sean correctas.',
                    icon: 'error',
                    confirmButtonText: 'Aceptar'
                });
            }
        });
    }
});
