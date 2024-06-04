$.getScript("/static/js/datatables.spanish.js", function() {       
    $(document).ready(function() {
        let editionSuccessful = false
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
            let idForm = $(this).data('id');
            cargarInformacionFormatoMedicamento(idForm);
        });

        function cargarInformacionFormatoMedicamento(id) {
            $.ajax({
                url: 'obtenerFormatoMedicamento/' + id + '/',
                type: 'GET',
                data: {},
                success: function(response) {
                    $('#formato').val(response.name);
                    $('#id').val(response.id);
                }
            });
        }


        function editarFormatoMedicamento(form) {
            var formData = $(form).serialize()
        
            // Enviar los datos al servidor usando AJAX
            $.ajax({
            url: "editarFormatoMedicamento/",
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
                alert("Ocurrió un error al editar el formato del medicamento")
            },
            })
        }


        $("#edicionFormatoMedicamentoForm").validate({
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
                editarFormatoMedicamento(form);
                return false // Esto previene el envío tradicional del formulario
            },
        });


        $("#modal-lg").on("hidden.bs.modal", function () {
            if (editionSuccessful) {
                Swal.fire({
                    title: 'Éxito',
                    text: 'El formato del medicamento fue editado correctamente.',
                    icon: 'success'
                });
            editionSuccessful = false;
            }
        })


        // Funcion para registrar un nuevo Tipo de Farmacia
        function registrarFormatoMedicamento(form) {
            var formData = $(form).serialize();
            $.ajax({
                url: "registrarFormatoMedicamento/",
                type: "POST",
                data: formData,
                headers: { "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val() },
                success: function(response) {
                    $("#modal-registrar-formato").modal("hide");
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
                                text: 'Ocurrió un error al registrar el formato del medicamento.',
                                icon: 'error'
                            });
                        }
                    }
                },
                error: function() {
                    Swal.fire({
                        title: 'Error',
                        text: 'Ocurrió un error al registrar el formato del medicamento.',
                        icon: 'error'
                    });
                },
            });
        }

        $("#registroFormatoMedicamentoForm").validate({
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
                registrarFormatoMedicamento(form);
                return false;
            },
        });

        $("#modal-registrar-formato").on("hidden.bs.modal", function () {
            if (registroSuccessful) {
                Swal.fire({
                    title: 'Éxito',
                    text: 'El formato del medicamento fue registrado correctamente.',
                    icon: 'success'
                });
                registroSuccessful = false;
            }
            // Limpiar el formulario del modal de registro
            $('#registroFormatoMedicamentoForm')[0].reset();
            $('#registroFormatoMedicamentoForm').find('.is-invalid').removeClass('is-invalid');
            $('#registroFormatoMedicamentoForm').find('.invalid-feedback').remove();
        });

        $('#registrarFormatoMedicamentoButton').on('click', function() {
            $('#modal-registrar-formato').modal('show');
        });


    });
});