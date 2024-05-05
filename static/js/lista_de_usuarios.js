$(document).ready(function() {

    var ajaxUrl = $('#miTabla').data('url');
    var table = $('#miTabla').DataTable({
        "ajax": ajaxUrl,
        "columns": [
            { "data": "index" },
            { "data": "first_name" },
            { "data": "last_name" },
            { "data": "username" },
            { "data": "email" },
            { "data": "first_group" },
            { "data": "is_active" },
            {
                "data": null,
                "orderable": false,
                "searchable": false,
                "render": function(data, type, row, meta) {
                    // Verifica si estás en la columna de acciones
                    if (meta.col === 7) { 
                        let editButton = `
                        <button id='editar' class='btn btn-sm btn-secondary' data-id='${row.username}' data-toggle='modal' data-target='#modal-lg'>
                            <i class="fas fa-pencil-alt"></i>
                        </button>&nbsp`
                        let deleteButton = `<button id='softdelete' class='btn btn-sm btn-danger' data-id='${row.username}'>
                        <i class="fa-solid fa-trash-can"></i>
                        </button>`
                        let restoreButton = `<button id='activar' class='btn btn-sm btn-secondary' data-id='${row.username}'>
                        <i class="fas fa-trash-restore-alt"></i>
                        </button>`
                        if(row.is_superuser) {
                            return editButton;
                        } else if(row.is_active) {
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
                "targets": 6, // Columna de estado activo
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
        var nombreUsuario = $(this).data('id'); 
        
        //Ejecuta el plugin (Sweet Alert) para confirmar la eliminación del usuario 
        Swal.fire({
            title: "¿Está seguro que desea eliminar a " + nombreUsuario + "?",
            icon: "question",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Aceptar"
          }).then((result) => {
            if (result.isConfirmed) {
                var id = $(this).data('id');
                deleteUser(id, $(this).closest('tr'));  
            }
          });
    });


    // Función AJAX para eliminar un usuario
    function deleteUser(id, row) {
        $.ajax({
            url: 'eliminarUsuario/' + id + '/',
            type: 'GET',
            data: {},
            success: function(response) {
                if (response.status == 'success') {
                    //Actualiza el estado del usuario eliminado
                    table.ajax.reload(null, false);
                    Swal.fire({
                        title: id + " ha sido eliminado satisfactoriamente!",
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
        var nombreUsuario = $(this).data('id');

        //Ejecuta el plugin (Sweet Alert) para confirmar la activación del usuario 
        Swal.fire({
            title: "¿Está seguro que desea activar a " + nombreUsuario + "?",
            icon: "question",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Aceptar"
          }).then((result) => {
            if (result.isConfirmed) {
                var id = $(this).data('id');
                activarUsuario(id, $(this).closest('tr')); 
              Swal.fire({
                title: "¡" + nombreUsuario + " ha sido activado satisfactoriamente!",
                icon: "success",
                confirmButtonColor: "#3085d6",
                confirmButtonText: "Aceptar"
              });
            }
          });
        
    });

    
    // Función AJAX para "Activar un usuario"
    function activarUsuario(id, row) {
        $.ajax({
            url: 'activarUsuario/' + id + '/',
            type: 'GET',
            data: {
                'username': id,
                'csrfmiddlewaretoken': '{{ csrf_token }}' // Token CSRF de Django
            },
            success: function(response) {
                if (response.status == 'success') {
                    // Actualiza el estado del usuario activado
                    table.ajax.reload(null, false);
                } else {
                    // Maneja el error
                    alert('No se pudo activar el usuario.');
                }
            }
        });
    }


     // Evento de clic en el botón "Editar"
     $('#miTabla').on('click', '#editar', function() {
        let nombreUsuario = $(this).data('id');
        
        cargarInformacionUsuario(nombreUsuario);
     });

     function cargarInformacionUsuario(id) {
        $.ajax({
            url: 'obtenerUsuario/' + id + '/',
            type: 'GET',
            data: {},
            success: function(response) {
                $('#nombre').val(response.name);
                $('#apellidos').val(response.lastname);
                $('#username').val(response.username);
            }
        });
    }

    $('#edicionUsuarioForm').on('submit', function(e) {
        e.preventDefault();
        var formData = $(this).serialize();
        // Enviar los datos al servidor usando AJAX
        $.ajax({
          url: 'editarUsuario/',
          type: 'POST',
          data: formData,
          headers: {'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()}, // Incluir el token CSRF
          success: function(response) {
            // Mostrar alerta de éxito
            alert('Usuario editado satisfactoriamente');
      
            // Refrescar DataTables
            $('#miTabla').DataTable().ajax.reload();
          },
          error: function(error) {
            alert('Ocurrió un error al editar el usuario');
          }
        });
      });
});

