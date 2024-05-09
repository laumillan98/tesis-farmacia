$(document).ready(function () {
    $('#backup-link').click(function (e) {
        e.preventDefault(); // Previene la acción por defecto del enlace
        var url = $(this).data('url'); // Obtiene la URL del atributo data-url
        $.ajax({
            type: 'GET',
            url: url,
            success: function (data) {
                if (data.status === 'success') {
                    Swal.fire('¡Éxito!', 'La copia de seguridad se realizó correctamente.', 'success');
                } else {
                    Swal.fire('Error', 'Ha ocurrido un error: ' + data.message, 'error');
                }
            },
            error: function () {
                Swal.fire('Error', 'Ha ocurrido un error al procesar la solicitud.', 'error');
            }
        });
    });
});