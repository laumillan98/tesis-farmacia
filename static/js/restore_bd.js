
$(document).ready(function () {
    $('#restore-link').click(function (e) {
        e.preventDefault(); // Previene la acción por defecto del enlace
        Swal.fire({
            title: "¿Está seguro que desea restaurar la BD ?",
            icon: "question",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Aceptar"
          }).then((result) => {
            if (result.isConfirmed) {
                var url = $(this).data('url'); // Obtiene la URL del atributo data-url
                $.ajax({
                    type: 'GET',
                    url: url,
                    success: function (data) {
                        if (data.status === 'success') {
                            Swal.fire('¡Éxito!', 'La restauración de la base de datos se realizó correctamente.', 'success');
                        } else {
                            Swal.fire('Error', 'Ha ocurrido un error al restaurar la base de datos: ' + data.message, 'error');
                        }
                    },
                    error: function () {
                        Swal.fire('Error', 'Ha ocurrido un error al procesar la solicitud.', 'error');
                    }
                });  
            }
          });
    });
});




  