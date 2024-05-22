$(document).ready(function() {
    let map;
    let marker;

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
                                    <button id="${mapaBtnId}" class="btn btn-info ver-mapa-btn" data-lat="${farmacia.latitud}" data-lng="${farmacia.longitud}">
                                        <i class="fa-solid fa-map-location-dot"></i>
                                    </button>
                                </td>
                            </tr>
                        `);
                    });

                    $('.ver-mapa-btn').click(function() {
                        var lat = $(this).data('lat');
                        var lng = $(this).data('lng');

                        $('#mapaModal').modal('show');

                        $('#mapaModal').on('shown.bs.modal', function() {
                            if (!map) {
                                map = L.map('mapa').setView([lat, lng], 13);

                                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                                }).addTo(map);

                                marker = L.marker([lat, lng]).addTo(map)
                                    .bindPopup('Ubicación de la farmacia')
                                    .openPopup();
                            } else {
                                map.setView([lat, lng], 13);
                                if (marker) {
                                    marker.setLatLng([lat, lng]);
                                } else {
                                    marker = L.marker([lat, lng]).addTo(map)
                                        .bindPopup('Ubicación de la farmacia')
                                        .openPopup();
                                }
                                setTimeout(function() {
                                    map.invalidateSize();
                                }, 400); // Agrega un pequeño retraso para asegurar que el modal esté completamente renderizado
                            }
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
});
