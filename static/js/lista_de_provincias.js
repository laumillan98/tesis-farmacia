$.getScript("/static/js/datatables.spanish.js", function() {    
    $(document).ready(function() {
        let editionSuccessful = false
        var ajaxUrl = $('#miTabla').data('url');
        var table = $('#miTabla').DataTable({
            "ajax": ajaxUrl,
            "columns": [
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
            let idProv = $(this).data('id');
            cargarInformacionProvincia(idProv);
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


        function editarProvincia(form) {
            var formData = $(form).serialize()
        
            // Enviar los datos al servidor usando AJAX
            $.ajax({
            url: "editarProvincia/",
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
                alert("Ocurrió un error al editar la provincia")
            },
            })
        }


        $("#edicionProvinciaForm").validate({
            rules: {
            nombre: {
                required: true,
                minlength: 3,
                pattern: /^[A-Za-z\s]+$/
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
                editarProvincia(form);
                return false // Esto previene el envío tradicional del formulario
            },
        });


        $("#modal-lg").on("hidden.bs.modal", function () {
            if (editionSuccessful) {
                Swal.fire({
                    title: 'Éxito',
                    text: 'La provincia fue editada correctamente.',
                    icon: 'success'
                });
            editionSuccessful = false;
            }
        })


        // Funcion para registrar Provincia
        function registrarProvincia(form) {
            var formData = $(form).serialize();
            $.ajax({
                url: "registrarProvincia/",
                type: "POST",
                data: formData,
                headers: { "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val() },
                success: function(response) {
                    $("#modal-registrar-provincia").modal("hide");
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
                                text: 'Ocurrió un error al registrar la provincia.',
                                icon: 'error'
                            });
                        }
                    }
                },
                error: function() {
                    Swal.fire({
                        title: 'Error',
                        text: 'Ocurrió un error al registrar la provincia.',
                        icon: 'error'
                    });
                },
            });
        }

        $("#registroProvinciaForm").validate({
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
                registrarProvincia(form);
                return false;
            },
        });

        $("#modal-registrar-provincia").on("hidden.bs.modal", function () {
            if (registroSuccessful) {
                Swal.fire({
                    title: 'Éxito',
                    text: 'La provincia fue registrada correctamente.',
                    icon: 'success'
                });
                registroSuccessful = false;
            }
            // Limpiar el formulario del modal de registro
            $('#registroProvinciaForm')[0].reset();
            $('#registroProvinciaForm').find('.is-invalid').removeClass('is-invalid');
            $('#registroProvinciaForm').find('.invalid-feedback').remove();
        });

        $('#registrarProvinciaButton').on('click', function() {
            $('#modal-registrar-provincia').modal('show');
        });

    });
});