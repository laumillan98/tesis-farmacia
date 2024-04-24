$(document).ready(function() {

    var ajaxUrl = $('#miTabla').data('url');
    var table = $('#miTabla').DataTable({
        "ajax": ajaxUrl,
        "columns": [
            { "data": "index" },
            { "data": "nombre" },
            { "data": "id_prov" },
            { "data": "id_munic" },
            { "data": "direccion" },
            { "data": "telefono" },
            { "data": "id_tipo" },
            { "data": "id_turno" },
            { "data": "is_active" },
            {
                "data": null,
                "orderable": false,
                "searchable": false,
                "render": function(data, type, row, meta) {
                    // Verifica si estás en la columna de acciones
                    if (meta.col === 9) { 
                        let editButton = `
                        <button id='editar' class='btn btn-sm btn-secondary' data-action='editar' data-id='${row.nombre}'>
                            <i class="fas fa-pencil-alt"></i>
                        </button>&nbsp`
                        let deleteButton = `<button id='softdelete' class='btn btn-sm btn-danger' data-id='${row.nombre}'>
                        <i class="fa-solid fa-trash-can"></i>
                        </button>`
                        let restoreButton = `<button id='activar' class='btn btn-sm btn-secondary' data-id='${row.nombre}' data-action='activar'>
                        <i class="fas fa-trash-restore-alt"></i>
                        </button>`
                        if(row.is_active) {
                            return editButton + deleteButton;
                        } else {
                            return restoreButton;
                        }
                    }
                    // Puedes retornar diferentes contenidos dependiendo de la columna
                    return data; // Retorna los datos originales para otras columnas
                }
            }
        ],
        "columnDefs": [
            {
                "targets": 8, // Columna de estado activo
                "orderable": false,
                "searchable": false,
                "render": function(data, type, row) {
                    return data ? '<i class="fas fa-check" style="color: green"></i>' : '<i class="fas fa-xmark" style="color: red"></i>';
                }
            },
        ]
    });

    // Evento de clic en el botón "Eliminar"
    $('#miTabla').on('click', '#softdelete', function() {
        var nombreFarma = $(this).data('id'); 
        
        //Ejecuta el plugin (Sweet Alert) para confirmar la eliminación de la farmacia 
        Swal.fire({
            title: "¿Está seguro que desea eliminar la farmacia " + nombreFarma + "?",
            icon: "question",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Aceptar"
          }).then((result) => {
            if (result.isConfirmed) {
                var id = $(this).data('id');
                deleteFarma(id, $(this).closest('tr'));  
            }
          });
    });


    // Función AJAX para eliminar una farmacia
    function deleteFarma(id, row) {
        $.ajax({
            url: 'eliminarFarmacia/' + id + '/',
            type: 'GET',
            data: {},
            success: function(response) {
                if (response.status == 'success') {
                    //Actualiza el estado de la farmacia eliminada
                    table.ajax.reload(null, false);
                    Swal.fire({
                        title: id + " ha sido eliminada satisfactoriamente!",
                        icon: "success",
                        confirmButtonColor: "#3085d6",
                        confirmButtonText: "Aceptar"
                    });
                } else {
                    // Maneja el error
                    alert('No se pudo eliminar el elemento.');
                }
            }
        });
    }


    // Evento de clic en el botón "Activar"
    $('#miTabla').on('click', '#activar', function() {
        var nombreFarmacia = $(this).data('id');

        //Ejecuta el plugin (Sweet Alert) para confirmar la activación de la farmacia 
        Swal.fire({
            title: "¿Está seguro que desea activar la farmacia " + nombreFarmacia + "?",
            icon: "question",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Aceptar"
          }).then((result) => {
            if (result.isConfirmed) {
                var id = $(this).data('id');
                activarFarmacia(id, $(this).closest('tr')); 
              Swal.fire({
                title: "¡" + nombreFarma + " ha sido activada satisfactoriamente!",
                icon: "success",
                confirmButtonColor: "#3085d6",
                confirmButtonText: "Aceptar"
              });
            }
          });
        
    });

    // Función AJAX para "Activar una farmacia"
    function activarFarmacia(id, row) {
        $.ajax({
            url: 'activarFarmacia/' + id + '/',
            type: 'GET',
            data: {
                'nombre': id,
                'csrfmiddlewaretoken': '{{ csrf_token }}' // Token CSRF de Django
            },
            success: function(response) {
                if (response.status == 'success') {
                    // Actualiza el estado de la farmacia activada
                    table.ajax.reload(null, false);
                } else {
                    // Maneja el error
                    alert('No se pudo activar la farmacia.');
                }
            }
        });
    }
});