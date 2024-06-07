$.getScript("/static/js/datatables.spanish.js", function() {   
    $(document).ready(function () {
        var ajaxUrl = $("#miTabla").data("url")
        var table = $("#miTabla").DataTable({
            ajax: {
                url: ajaxUrl,
                dataSrc: 'data'
            },
            columns: [
                { data: "index" },
                { data: "nombre" },
                { data: "formato" },
                { data: "precio" },
                { data: "origen" },
                { data: "restriccion" },
                { data: "clasificacion" },
                { data: "existencia"},
                {
                    data: null,
                    orderable: false,
                    searchable: false,
                    render: function (data, type, row, meta) {
                        let mostrarButton = `
                        <button id='mostrar' class='btn btn-sm btn-info' data-id='${row.id}' data-toggle='modal' data-target='#modaldesc-lg'>
                            <i class="fa-solid fa-eye"></i>
                        </button>`;
                        return mostrarButton;
                    }
                },
            ]
        });

        
        // Evento de clic en el botón "Mostrar" Descripcion
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
                    $('#descripcionMostrar').text(response.description);
                    $('#id').val(response.id);
                    $('#modaldesc-lg').modal('show'); 
                },
            })
        }

    });
    
});