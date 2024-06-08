$.getScript("/static/js/datatables.spanish.js", function() {  
    $(document).ready(function () {
        var ajaxUrl = $("#miTabla").data("url");
        var table = $("#miTabla").DataTable({
            processing: true,
            serverSide: true,
            ajax: {
            'url': ajaxUrl,
            'type': "GET",
            "data": function(d) {
                d.page = (d.start / d.length) + 1;  // Agregar el número de página al request
                d.nombre = $('#nombre').val();
                d.clasificacion = $('#clasificacion').val();
                d.formato = $('#formato').val();
                d.restriccion = $('#restriccion').val();
                d.origen = $('#origen').val();
            }
            },
            columns: [
                { data: "index" },
                { data: "nombre" },
                { data: "formato" },
                { data: "cant_max" },
                { data: "precio_unidad" },
                { data: "origen" },
                { data: "restriccion" },
                { data: "clasificacion" },
                {
                    data: null,
                    orderable: false,
                    searchable: false,
                    render: function (data, type, row, meta) {
                        let mostrarButton = `
                        <button id='mostrar' class='btn btn-sm btn-info mr-2' data-id='${row.id}' data-toggle='modal' data-target='#modaldesc-lg'>
                            <i class="fa-solid fa-eye"></i>
                        </button>`;
                        let reacButton = `
                        <button id='mostrarReac' class='btn btn-sm btn-warning' data-id='${row.id}' data-toggle='modal' data-target='#modalreac-lg'>
                            <i class="fa-solid fa-triangle-exclamation fa-beat"></i>
                        </button>`;
                        return mostrarButton + reacButton;
                    }
                },
                {
                data: null,
                orderable: false,
                searchable: false,
                render: function (data, type, row, meta) {
                    let exportButton = `
                    <button id='exportar' class='btn btn-sm btn-primary' data-id='${row.id}' data-toggle='modal' data-target='#modal-lg'>
                        <i class="fa-solid fa-file-export"></i>
                    </button>`;
                    return exportButton;
                }
                },
            ],
        });


        // Evento de clic en el botón "Mostrar Descripcion"
        $('#miTabla').on('click', '#mostrar', function() {
            let idMedic = $(this).data('id');
            cargarDescripcionMedicamento(idMedic);
        });

        function cargarDescripcionMedicamento(id) {
            $.ajax({
                url: 'obtenerDescripcion/' + id + '/',
                type: 'GET',
                data: {},
                success: function(response) {
                    $('#descripcionMostrar').html(response.description);
                    $('#id').val(response.id);
                    $('#modaldesc-lg').modal('show'); 
                },
            })
        }


        // Evento de clic en el botón "Mostrar Reacciones"
        $('#miTabla').on('click', '#mostrarReac', function() {
            let idMedic = $(this).data('id');
            cargarReaccionesMedicamento(idMedic);
        });

        function cargarReaccionesMedicamento(id) {
            $.ajax({
                url: 'obtenerReacciones/' + id + '/',
                type: 'GET',
                data: {},
                success: function(response) {
                    $('#reaccionesMostrar').html(response.reacciones);
                    $('#id').val(response.id);
                    $('#modalreac-lg').modal('show'); 
                },
            })
        }


        // Evento de clic en el botón "Exportar"
        $('#miTabla').on('click', '#exportar', function() {
            let idMedic = $(this).data('id');
            exportarMedicamento(idMedic);
        });

        function exportarMedicamento(id, row) {
            $.ajax({
                url: 'exportarMedicamento/' + id + '/',
                type: 'POST',
                data: {},
                headers: { 'X-CSRFToken': '{{ csrf_token }}' },  
                success: function(response) {
                    if (response.status === 'success') {
                        // Eliminar la fila de la tabla sin recargar la página
                        table.row(row).remove().draw(false);

                        Swal.fire({
                            title: 'Exportado',
                            text: 'El medicamento ha sido exportado a tu farmacia con éxito.',
                            icon: 'success',
                            confirmButtonText: 'Aceptar'
                        });
                    } else {
                        Swal.fire({
                            title: 'Error',
                            text: response.message,
                            icon: 'error',
                            confirmButtonText: 'Aceptar'
                        });
                    }
                },
                error: function(response) {
                    Swal.fire({
                        title: 'Error',
                        text: 'No se pudo exportar el medicamento. Inténtalo nuevamente.',
                        icon: 'error',
                        confirmButtonText: 'Aceptar'
                    });
                }
            });
        }
    });
}); 