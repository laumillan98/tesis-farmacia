$.getScript("/static/js/datatables.spanish.js", function() {  
    $(document).ready(function () {
        let editionSuccessful = false;
        var ajaxUrl = $("#miTabla").data("url");
        var table = $("#miTabla").DataTable({
            processing: true,
            serverSide: true,
            ajax: {
              'url': ajaxUrl,
              'type': "GET",
              "data": function(d) {
                d.page = (d.start / d.length) + 1;  // Agregar el número de página al request
              }
            },
            columns: [
                { data: "index" },
                { data: "factura" },
                { data: "numero_lote" },
                { data: "cantidad" },
                { data: "fecha_creacion"},
                { data: "fecha_elaboracion" },
                { data: "fecha_vencimiento" },
                { data: "medicamento_nombre" },
                {
                    data: null,
                    orderable: false,
                    searchable: false,
                    render: function (data, type, row, meta) {
                        let editButton = `
                        <button id='editar' class='btn btn-sm btn-success' data-id='${row.id}' data-toggle='modal' data-target='#modal-lg'>
                            <i class="fas fa-pencil-alt"></i>
                        </button>`;
                        return editButton;
                    }
                },
            ],
        });
  
        // Evento de clic en el botón "Editar"
        $('#miTabla').on('click', '#editar', function() {
            let idEntrada = $(this).data('id');
            cargarInformacionEntrada(idEntrada);
        });
        
        function cargarInformacionEntrada(id) {
            $.ajax({
                url: 'obtenerEntradaMedicamento/' + id + '/',
                type: 'GET',
                data: {},
                success: function(response) {
                    $('#factura').val(response.factura);
                    $('#numero_lote').val(response.numero_lote);
                    $('#cantidad').val(response.cantidad);
                    $('#fecha_creacion').val(response.fecha_creacion);
                    $('#fecha_elaboracion').val(response.fecha_elaboracion);
                    $('#fecha_vencimiento').val(response.fecha_vencimiento);
                    $('#medicamento_nombre').val(response.medicamento_nombre);
                    $('#id').val(response.id);
                },
            })
        }
  
        function editarEntrada(form) {
            var formData = $(form).serialize()
        
            // Enviar los datos al servidor usando AJAX
            $.ajax({
              url: "editarEntradaMedicamento/",
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
                alert("Ocurrió un error al editar la entrada")
              },
            })
        }

        $.validator.addMethod("validFechaCreacion", function(value, element) {
            let fechaCreacion = new Date(value);
            let today = new Date();
            return fechaCreacion <= today; // Verificar que la fecha de creación no sea posterior a la fecha actual
        }, "La fecha de creación no puede ser posterior a la fecha actual");
  
        $.validator.addMethod("validFechaElaboracion", function(value, element) {
            let fechaElaboracion = new Date(value);
            let today = new Date();
            return fechaElaboracion <= today; // Verificar que la fecha de elaboración no sea posterior a la fecha actual
        }, "La fecha de elaboración no puede ser posterior a la fecha actual");
  
        $.validator.addMethod("validFechaVencimiento", function(value, element) {
            let fechaVencimiento = new Date(value);
            let today = new Date();
            return fechaVencimiento > today; // Verificar que la fecha de vencimiento sea mayor que la fecha actual
        }, "La fecha de vencimiento debe ser mayor que la fecha actual");
  
        $.validator.addMethod("validFechaEntreUnAno", function(value, element, params) {
            let fechaElaboracion = new Date($(params).val());
            let fechaVencimiento = new Date(value);
            let diff = fechaVencimiento - fechaElaboracion;
            let oneYear = 365 * 24 * 60 * 60 * 1000;
            return diff >= oneYear; // Verificar que la diferencia entre las fechas sea de al menos un año
        }, "La diferencia entre la fecha de elaboración y la fecha de vencimiento debe ser de al menos un año");
  
        $("#edicionEntradaForm").validate({
            rules: {
                factura: {
                    required: true,
                    minlength: 3,
                    maxlength: 20,
                    pattern: /^[A-Za-z0-9]+$/ 
                },
                numero_lote: {
                    required: true,
                    minlength: 3,
                    maxlength: 20,
                    pattern: /^[A-Za-z0-9]+$/ 
                },
                cantidad: {
                    required: true,
                    minlength: 1,
                    maxlength: 3,
                    digits: true
                },
                fecha_creacion: {
                    required: true,
                    date: true,
                    validFechaCreacion: true
                },
                fecha_elaboracion: {
                    required: true,
                    date: true,
                    validFechaElaboracion: true
                },
                  fecha_vencimiento: {
                    required: true,
                    date: true,
                    validFechaVencimiento: true,
                    validFechaEntreUnAno: '#fecha_elaboracion' // Validar con respecto a fecha de elaboración
                },
            },
  
            messages: {
                factura: {
                    required: "Este campo es obligatorio.",
                    minlength: "Por favor, introduce al menos 3 caracteres.",
                    maxlength: "Por favor, no introduzcas más de 20 caracteres.",
                    pattern: "Por favor introduce una factura válida (solo letras y números)."
                },
                numero_lote: {
                    required: "Este campo es obligatorio.",
                    minlength: "Por favor, introduce al menos 3 caracteres.",
                    maxlength: "Por favor, no introduzcas más de 20 caracteres.",
                    pattern: "Por favor introduce un número de lote válido (solo letras y números)."
                },
                cantidad: {
                    required: "Este campo es obligatorio.",
                    minlength: "Solo puede contener de 1 a 3 dígitos.",
                    maxlength: "Solo puede contener de 1 a 3 dígitos.",
                    digits: "No puede contener letras ni símbolos."
                },
                fecha_creacion: {
                    required: "Este campo es obligatorio.",
                    date: "Por favor introduce una fecha válida.",
                    validFechaCreacion: "La fecha de creación no puede ser futura."
                },
                fecha_elaboracion: {
                    required: "Este campo es obligatorio.",
                    date: "Por favor introduce una fecha válida.",
                    validFechaElaboracion: "La fecha de elaboración no puede ser posterior a la fecha actual."
                },
                 fecha_vencimiento: {
                    required: "Este campo es obligatorio.",
                    date: "Por favor introduce una fecha válida.",
                    validFechaVencimiento: "La fecha de vencimiento debe ser mayor que la fecha actual.",
                    validFechaEntreUnAno: "La diferencia entre la fecha de elaboración y la fecha de vencimiento debe ser de al menos un año."
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
                editarEntrada(form);
                return false // Esto previene el envío tradicional del formulario
            },
        });
  
        $("#modal-lg").on("hidden.bs.modal", function () {
            if (editionSuccessful) {
                Swal.fire({
                    title: 'Éxito',
                    text: 'La entrada fue editada correctamente.',
                    icon: 'success'
                });
                editionSuccessful = false;
            }
        });
    });
});
