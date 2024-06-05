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
                //{ data: "cant_max" },
                { data: "precio" },
                { data: "origen" },
                { data: "restriccion" },
                { data: "clasificacion" },
                {
                    data: "fecha_expiracion",
                    orderable: false,
                    searchable: false,
                    render: function(data, type, row) {
                        return '<input style="width: 125px; display: inline;" type="date" class="form-control fecha-editable" value="' + data + '" data-id="' + row.id + '" />' +
                            '<button class="btn btn-sm btn-success btn-guardar-fecha" style="margin-left: 5px;" data-id="' + row.id + '"><i class="fa-solid fa-calendar-days"></i></button>';
                    }
                },
                {
                    data: "existencia",
                    orderable: false,
                    searchable: false,
                    render: function(data, type, row) {
                        // Renderizar un input editable para existencia con validación para no aceptar valores menores a 0
                        return '<input type="number" class="form-control existencia-editable" style="width: 60px; display: inline;" min="0" value="' + data + '" data-id="' + row.id + '" />' +
                            '<button class="btn btn-sm btn-success btn-guardar" style="margin-left: 5px;" data-id="' + row.id + '">Guardar</button>';
                    }
                },
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
                }
            ]
        });


        // Manejar clic en el botón de guardar fecha de expiración
        $('#miTabla').on('click', '.btn-guardar-fecha', function() {
            var id_medic = $(this).data('id');
            var fechaInput = $(this).closest('td').find('.fecha-editable');
            var fecha_expiracion = fechaInput.val();

            // Validar que la fecha de expiración sea futura
            var today = new Date().toISOString().split('T')[0];
            if (fecha_expiracion <= today) {
                Swal.fire({
                    icon: 'error',
                    title: 'Fecha inválida',
                    text: 'La fecha de expiración debe ser una fecha futura.'
                });
                return; // Detener la ejecución si la fecha es inválida
            }

            // Realizar una solicitud AJAX para actualizar la fecha de expiración
            $.ajax({
                url: '/actualizar_fecha_expiracion/',
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                data: { 'id_medic': id_medic, 'fecha_expiracion': fecha_expiracion },
                success: function(response) {
                    console.log('Fecha de expiración actualizada correctamente');
                    table.ajax.reload();
                    Swal.fire({
                        icon: 'success',
                        title: 'Fecha de expiración actualizada',
                        text: 'La fecha de expiración se ha actualizado correctamente.'
                    });
                },
                error: function(error) {
                    console.error('Error al actualizar fecha de expiración');
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Ocurrió un error al actualizar la fecha de expiración.'
                    });
                }
            });
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


        // Manejar clic en el botón de guardar existencia
        $('#miTabla').on('click', '.btn-guardar', function() {
            var id_medic = $(this).data('id');
            var existenciaInput = $(this).closest('td').find('.existencia-editable');
            var existencia = existenciaInput.val();

            // Validar que la existencia no sea menor que 0
            if (existencia < 0) {
                Swal.fire({
                    icon: 'error',
                    title: 'Valor inválido',
                    text: 'La existencia no puede ser menor que 0.'
                });
                return; // Detener la ejecución si el valor es inválido
            }

            // Realizar una solicitud AJAX para actualizar la existencia
            $.ajax({
                url: '/actualizar_existencia/',
                method: 'POST',
                headers: { 'X-CSRFToken': getCookie('csrftoken') },
                data: { 'id_medic': id_medic, 'existencia': existencia },
                success: function(response) {
                    console.log('Existencia actualizada correctamente');
                    // Actualizar la tabla después de la edición
                    table.ajax.reload();

                    // Mostrar Sweet Alert de éxito
                    Swal.fire({
                        icon: 'success',
                        title: 'Existencia actualizada',
                        text: 'La existencia se ha actualizado correctamente.'
                    });
                },
                error: function(error) {
                    console.error('Error al actualizar existencia');
                    // Mostrar Sweet Alert de error
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Ocurrió un error al actualizar la existencia.'
                    });
                }
            });
        });

        
        // Función para obtener el valor de una cookie por su nombre
        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = cookies[i].trim();
                    // Obtener el valor de la cookie si coincide con el nombre
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }


        // Función para agregar los medicamentos seleccionados
        $('#agregarMedicamentosBtn').on('click', function() {
            var selectedMedicamentos = [];
            $('input[name="medicamentos_seleccionados"]:checked').each(function() {
                selectedMedicamentos.push($(this).val());
            });

            $.ajax({
                url: '/agregar_medicfarma/',
                type: 'POST',
                headers: {
                    'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val()
                },
                data: {
                    'medicamentos': selectedMedicamentos,
                    'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
                },
                success: function(response) {
                    // Manejar la respuesta del servidor si es necesario
                    console.log('Medicamentos agregados exitosamente');
                },
                error: function(error) {
                    console.log('Error al agregar medicamentos');
                }
            });
        });

    });
});