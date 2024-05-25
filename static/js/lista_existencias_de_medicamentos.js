$(document).ready(function() {
    let map;
    let marker;
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

                        $('#mapaModal').on('shown.bs.modal', function() {
                            getUserLocation();
                        });
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
        if (map) {
            setTimeout(function() {
                map.invalidateSize();
            }, 100);
        }
    });

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

                if (map) {
                    map.remove();
                }
                map = L.map('mapa').setView([userLat, userLng], 13);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; OpenStreetMap contributors'
                }).addTo(map);

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
