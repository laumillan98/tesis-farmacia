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
                    $('#descripcionMostrar').html(response.description);
                    $('#id').val(response.id);
                    $('#modaldesc-lg').modal('show'); 
                },
            })
        }


        // Evento de clic en el botón Reacciones
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

    });
    
});