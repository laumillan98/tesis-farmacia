$(document).ready(function() {
    let map;
    let markers = [];
    let farmaciaData = [];
    let municipioCenter = [20, -75]; // Coordenadas centrales predeterminadas para Cuba

    $('#buscarFarmaciaBtn').click(function() {
        var nombreMunicipio = $('#nombre_municipio').val();

        $.ajax({
            url: buscarFarmaciaUrl,
            type: "GET",
            data: { nombre_municipio: nombreMunicipio },
            success: function(response) {
                var resultadosTabla = $('#resultadosTabla tbody');
                resultadosTabla.empty();
                farmaciaData = response;

                if (response.length > 0) {
                    $.each(response, function(index, farmacia) {
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
                                <td>
                                    <button id="${mapaBtnId}" class="btn btn-info ver-mapa-btn" data-lat="${farmacia.latitud}" data-lng="${farmacia.longitud}" data-nombre="${farmacia.nombre_farmacia}">
                                        <i class="fa-solid fa-map-location-dot"></i>
                                    </button>
                                </td>
                            </tr>
                        `);
                    });

                    $('#verMapaBtn').show();

                    // Definir el centro del municipio basado en la primera farmacia de la lista
                    municipioCenter = [response[0].latitud, response[0].longitud];

                    $('.ver-mapa-btn').click(function() {
                        var lat = $(this).data('lat');
                        var lng = $(this).data('lng');
                        var nombreFarmacia = $(this).data('nombre');

                        $('#mapaModal').modal('show');

                        $('#mapaModal').on('shown.bs.modal', function() {
                            if (!map) {
                                map = L.map('mapa').setView([lat, lng], 13);

                                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                                }).addTo(map);

                                var marker = L.marker([lat, lng]).addTo(map)
                                    .bindPopup("Farmacia " + nombreFarmacia)
                                    .openPopup();
                                markers.push(marker);
                            } else {
                                map.setView([lat, lng], 13);
                                if (markers.length > 0) {
                                    markers.forEach(function(marker) {
                                        map.removeLayer(marker);
                                    });
                                }
                                var marker = L.marker([lat, lng]).addTo(map)
                                    .bindPopup("Farmacia " + nombreFarmacia)
                                    .openPopup();
                                markers.push(marker);
                                setTimeout(function() {
                                    map.invalidateSize();
                                }, 400);
                            }
                        });
                    });
                } else {
                    $('#verMapaBtn').hide();
                    Swal.fire({
                        title: 'No encontrado',
                        text: 'No se encontraron farmacias en el municipio buscado.',
                        icon: 'info',
                        confirmButtonText: 'Aceptar'
                    });
                }
            },
            error: function(response) {
                Swal.fire({
                    title: 'Error',
                    text: 'Debe introducir un municipio para poder realizar la búsqueda.',
                    icon: 'error',
                    confirmButtonText: 'Aceptar'
                });
            }
        });
    });

    $('#verMapaBtn').click(function() {
        $('#mapaModal').modal('show');

        $('#mapaModal').on('shown.bs.modal', function() {
            if (!map) {
                map = L.map('mapa').setView(municipioCenter, 13);

                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                }).addTo(map);

                farmaciaData.forEach(function(farmacia) {
                    if (farmacia.latitud && farmacia.longitud) {
                        var marker = L.marker([farmacia.latitud, farmacia.longitud]).addTo(map)
                            .bindPopup("Farmacia " + farmacia.nombre_farmacia)
                            .openPopup();
                        markers.push(marker);
                    }
                });
            } else {
                map.setView(municipioCenter, 13);
                if (markers.length > 0) {
                    markers.forEach(function(marker) {
                        map.removeLayer(marker);
                    });
                    markers = [];
                }
                farmaciaData.forEach(function(farmacia) {
                    if (farmacia.latitud && farmacia.longitud) {
                        var marker = L.marker([farmacia.latitud, farmacia.longitud]).addTo(map)
                            .bindPopup("Farmacia " + farmacia.nombre_farmacia)
                            .openPopup();
                        markers.push(marker);
                    }
                });
                setTimeout(function() {
                    map.invalidateSize();
                }, 400);
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
});
