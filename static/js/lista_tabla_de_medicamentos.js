$(document).ready(function() {
    $('#buscarMedicamentoBtn').click(function() {
        var nombreMedicamento = $('#nombre_medicamento').val();

        $.ajax({
            url: buscarinfoMedicamentoUrl,
            type: "GET",
            data: { nombre_medicamento: nombreMedicamento },
            success: function(response) {
                var resultadosTabla = $('#resultadosTabla tbody');
                resultadosTabla.empty();

                if (response.length > 0) {
                    $.each(response, function(index, medicamento) {

                        resultadosTabla.append(`
                            <tr>
                                <td>${index + 1}</td>
                                <td>${medicamento.nombre}</td>
                                <td>${medicamento.formato}</td>
                                <td>${medicamento.cant_max}</td>
                                <td>${medicamento.precio_unidad}</td>
                                <td>${medicamento.origen}</td>
                                <td>${medicamento.restriccion}</td>
                                <td>${medicamento.clasificacion}</td>
                                <td>
                                    <button class='btn btn-sm btn-info mostrar-descripcion-btn' data-id='${medicamento.id}' data-toggle='modal' data-target='#modaldesc-lg'>
                                        <i class="fa-solid fa-eye"></i>
                                    </button>
                                </td>
                            </tr>
                        `);
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

    // Evento de clic en el botón "Mostrar Descripcion"
    $(document).on('click', '.mostrar-descripcion-btn', function() {
        let idMedic = $(this).data('id');
        cargarDescripcionMedicamento(idMedic);
    });
  
    function cargarDescripcionMedicamento(id) {
        $.ajax({
            url: 'obtenerDescripcion/' + id + '/',
            type: 'GET',
            data: {},
            success: function(response) {
                $('#descripcionMostrar').text(response.description);
                $('#id').val(response.id);
                $('#modaldesc-lg').modal('show'); 
            },
        })
    }

});