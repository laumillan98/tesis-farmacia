$.getScript("/static/js/datatables.spanish.js", function() {    
   $(document).ready(function() {
        let editionSuccessful = false
        let registroSuccessful = false
        var ajaxUrl = $('#miTabla').data('url');
        var table = $('#miTabla').DataTable({
            ajax: ajaxUrl,
            columns: [
                { data: "index" },
                { data: "nombre" },
                {
                    data: null,
                    orderable: false,
                    searchable: false,
                    render: function(data, type, row, meta) {
                        // Verifica si estás en la columna de acciones
                        if (meta.col === 2) { 
                            let editButton = `
                            <button id='editar' class='btn btn-sm btn-success' data-id='${row.id}' data-toggle='modal' data-target='#modal-lg'>
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
            let idTurn = $(this).data('id');
            cargarInformacionTurnoFarmacia(idTurn);
        });

        function cargarInformacionTurnoFarmacia(id) {
            $.ajax({
                url: 'obtenerTurnoFarmacia/' + id + '/',
                type: 'GET',
                data: {},
                success: function(response) {
                    $('#turno').val(response.name);
                    $('#id').val(response.id);
                }
            });
        }


        function editarTurnoFarmacia(form) {
            var formData = $(form).serialize()
        
            // Enviar los datos al servidor usando AJAX
            $.ajax({
                url: "editarTurnoFarmacia/",
                type: "POST",
                data: formData,
                headers: { "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val() }, // Incluir el token CSRF
                success: function (response) {
                    $("#modal-lg").modal("hide")
            
                    // Mostrar alerta de éxito
                    if (response.success === true) {
                    editionSuccessful = true
                    // Refrescar DataTables
                    $("#miTabla").DataTable().ajax.reload()
                    }
                },
                error: function (error) {
                    alert("Ocurrió un error al editar el turno de la farmacia")
                },
            })
        }


        $("#edicionTurnoFarmaciaForm").validate({
            rules: {
            nombre: {
                required: true,
                minlength: 3,
                pattern: /^[A-Za-záéíóúÁÉÍÓÚüÜ\s]+$/
            },
            },
            messages: {
                nombre: {
                    required: "Este campo es obligatorio.",
                    minlength: "Por favor, introduce al menos 3 caracteres.",
                    pattern: "No puede contener números ni símbolos."
                },
            },
            errorElement: 'span',
            errorPlacement: function (error, element) {
                error.addClass('invalid-feedback');
                element.closest('.form-group').append(error);
            },
            highlight: function (element, errorClass, validClass) {
                $(element).addClass('is-invalid');
            },
            unhighlight: function (element, errorClass, validClass) {
                $(element).removeClass('is-invalid');
            },
            submitHandler: function (form) {
                editarTurnoFarmacia(form);
                return false // Esto previene el envío tradicional del formulario
            },
        });


        $("#modal-lg").on("hidden.bs.modal", function () {
            if (editionSuccessful) {
                Swal.fire({
                    title: 'Éxito',
                    text: 'El turno de la farmacia fue editado correctamente.',
                    icon: 'success'
                });
            editionSuccessful = false;
            }
        })


        // Funcion para registrar un nuevo Turno de Farmacia
        function registrarTurnoFarmacia(form) {
            var formData = $(form).serialize();
            $.ajax({
                url: "registrarTurnoFarmacia/",
                type: "POST",
                data: formData,
                headers: { "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val() },
                success: function(response) {
                    $("#modal-registrar-turno").modal("hide");
                    if (response.success === true) {
                        registroSuccessful = true;
                        $("#miTabla").DataTable().ajax.reload();
                    } else {
                        if (response.errors && response.errors.nombre) {
                            Swal.fire({
                                title: 'Error',
                                text: response.errors.nombre[0],
                                icon: 'error'
                            });
                        } else {
                            Swal.fire({
                                title: 'Error',
                                text: 'Ocurrió un error al registrar el turno de la farmacia.',
                                icon: 'error'
                            });
                        }
                    }
                },
                error: function() {
                    Swal.fire({
                        title: 'Error',
                        text: 'Ocurrió un error al registrar el turno de la farmacia.',
                        icon: 'error'
                    });
                },
            });
        }

        $("#registroTurnoFarmaciaForm").validate({
            rules: {
                nombre: {
                    required: true,
                    minlength: 3,
                    maxlength: 20,
                    pattern: /^[A-Za-záéíóúÁÉÍÓÚüÜ\s]+$/
                },
            },
            messages: {
                nombre: {
                    required: "Este campo es obligatorio.",
                    minlength: "Por favor, introduce al menos 3 caracteres.",
                    maxlength: "No puede contener más de 20 caracteres.",
                    pattern: "No puede contener números ni símbolos."
                },
            },
            errorElement: 'span',
            errorPlacement: function (error, element) {
                error.addClass('invalid-feedback');
                element.closest('.form-group').append(error);
            },
            highlight: function (element, errorClass, validClass) {
                $(element).addClass('is-invalid');
            },
            unhighlight: function (element, errorClass, validClass) {
                $(element).removeClass('is-invalid');
            },
            submitHandler: function (form) {
                registrarTurnoFarmacia(form);
                return false;
            },
        });

        $("#modal-registrar-turno").on("hidden.bs.modal", function () {
            if (registroSuccessful) {
                Swal.fire({
                    title: 'Éxito',
                    text: 'El turno de farmacia fue registrado correctamente.',
                    icon: 'success'
                });
                registroSuccessful = false;
            }
            // Limpiar el formulario del modal de registro
            $('#registroTurnoFarmaciaForm')[0].reset();
            $('#registroTurnoFarmaciaForm').find('.is-invalid').removeClass('is-invalid');
            $('#registroTurnoFarmaciaForm').find('.invalid-feedback').remove();
        });

        $('#registrarTurnoFarmaciaButton').on('click', function() {
            $('#modal-registrar-turno').modal('show');
        });


    });
});