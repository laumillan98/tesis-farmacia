$(document).ready(function() {

    var ajaxUrl = $('#miTabla').data('url');
    var table = $('#miTabla').DataTable({
        "ajax": ajaxUrl,
        "columns": [
            { "data": "index" },
            { "data": "id" },
            { "data": "nombre" },
            {
                "data": null,
                "orderable": false,
                "searchable": false,
                "render": function(data, type, row, meta) {
                    // Verifica si estás en la columna de acciones
                    if (meta.col === 3) { 
                        let editButton = `
                        <button id='editar' class='btn btn-sm btn-secondary' data-id='${row.id}' data-toggle='modal' data-target='#modal-lg'>
                            <i class="fas fa-pencil-alt"></i>
                        </button>&nbsp`
                        return editButton;
                    }
                    // Puedes retornar diferentes contenidos dependiendo de la columna
                    return data; // Retorna los datos originales para otras columnas
                }
            }
        ],
    });


     // Evento de clic en el botón "Editar"
     $('#miTabla').on('click', '#editar', function() {
        let nombreProv = $(this).data('id');
        cargarInformacionProvincia(nombreProv);
     });

     function cargarInformacionProvincia(id) {
        $.ajax({
            url: 'obtenerProvincia/' + id + '/',
            type: 'GET',
            data: {},
            success: function(response) {
                $('#provincia').val(response.name);
                $('#id').val(response.id);
            }
        });
    }

    $('#edicionProvinciaForm').on('submit', function(e) {
        alert('Provincia editada satisfactoriamente');
        e.preventDefault();
        var formData = $(this).serialize();
      
        // Enviar los datos al servidor usando AJAX
        $.ajax({
          url: 'editarProvincia/',
          type: 'POST',
          data: formData,
          headers: {'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()}, // Incluir el token CSRF
          success: function(response) {
            // Mostrar alerta de éxito
            alert('Provincia editada satisfactoriamente');
      
            // Refrescar DataTables
            $('#miTabla').DataTable().ajax.reload();
          },
          error: function(error) {
            alert('Ocurrió un error al editar la provincia');
          }
        });
      });
});