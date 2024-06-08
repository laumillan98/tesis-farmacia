$.getScript("/static/js/datatables.spanish.js", function() {  
    $(document).ready(function () {
        let registroSuccessful = false;
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
                { data: "medicamento_formato" },
            ],
        });


        // Abrir el modal para registrar una nueva entrada
        $('#registrarEntradaButton').on('click', function() {
            $('#modal-registrar-entrada').modal('show');
            $('#registroEntradaForm').trigger("reset");
            $('.select2').val(null).trigger('change');
        });
        
        function registrarEntrada(form) {
            var formData = $(form).serialize();
        
            $.ajax({
                url: "registrarEntradaMedicamento/",
                type: "POST",
                data: formData,
                headers: { "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val() },
                success: function (response) {
                    if (response.success === true) {
                        registroSuccessful = true;
                        $("#modal-registrar-entrada").modal("hide");
                        $("#miTabla").DataTable().ajax.reload();
                    } else { 
                        Swal.fire({
                            title: 'Error',
                            text: 'Ocurrió un error al registrar la entrada',
                            icon: 'error'
                        });
                    }
                },
                error: function (error) {
                    Swal.fire({
                        title: 'Error',
                        text: 'Ocurrió un error al registrar la entrada',
                        icon: 'error'
                    });
                },
            });
        }

        $.validator.addMethod("validFechaElaboracion", function(value, element) {
            let fechaElaboracion = new Date(value);
            let today = new Date();
            let oneMonthAgo = new Date(today.setMonth(today.getMonth() - 1));
            return fechaElaboracion < today && fechaElaboracion <= oneMonthAgo; 
        }, "La fecha de elaboración debe ser al menos un mes antes de la fecha actual");
  
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

        $.validator.addMethod("validCantidad", function(value, element) {
            return value > 0; // Verificar que la cantidad sea mayor que cero
        }, "La cantidad debe ser mayor que cero");

        $.validator.addMethod("validFactura", function(value, element) {
            return /^\d{8}$/.test(value); // Verificar que la factura tenga exactamente 8 dígitos
        }, "Factura no válida, debe contener exactamente 8 dígitos numéricos");

        
        $("#registroEntradaForm").validate({
            rules: {
                factura: {
                    required: true,
                    validFactura: true
                },
                numero_lote: {
                    required: true,
                    minlength: 6,
                    maxlength: 12,
                    pattern: /^[A-Za-z0-9]+$/ 
                },
                cantidad: {
                    required: true,
                    minlength: 1,
                    maxlength: 3,
                    digits: true,
                    validCantidad: true
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
                    validFechaEntreUnAno: '#nuevaFechaElaboracion' // Validar con respecto a fecha de elaboración
                },
                id_farmaciaMedicamento: {
                    required: true,
                }
            },

            messages: {
                factura: {
                    required: "Este campo es obligatorio.",
                    validFactura: "Factura no válida, debe contener exactamente 8 dígitos numéricos"
                },
                numero_lote: {
                    required: "Este campo es obligatorio.",
                    minlength: "Por favor, introduce al menos 6 caracteres.",
                    maxlength: "Por favor, no introduzcas más de 12 caracteres.",
                    pattern: "Por favor introduce un número de lote válido (solo letras y números)."
                },
                cantidad: {
                    required: "Este campo es obligatorio.",
                    minlength: "Solo puede contener de 1 a 3 dígitos.",
                    maxlength: "Solo puede contener de 1 a 3 dígitos.",
                    digits: "No puede contener letras ni símbolos.",
                    validCantidad: "La cantidad debe ser mayor que cero."
                },
                fecha_elaboracion: {
                    required: "Este campo es obligatorio.",
                    date: "Por favor introduce una fecha válida.",
                    validFechaElaboracion: "La fecha de elaboración debe ser al menos un mes antes de la fecha actual."
                },
                fecha_vencimiento: {
                    required: "Este campo es obligatorio.",
                    date: "Por favor introduce una fecha válida.",
                    validFechaVencimiento: "La fecha de vencimiento debe ser mayor que la fecha actual.",
                    validFechaEntreUnAno: "La diferencia entre la fecha de elaboración y la fecha de vencimiento debe ser de al menos un año."
                },
                id_farmaciaMedicamento: {
                    required: "Este campo es obligatorio.",
                }
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
                registrarEntrada(form);
                return false; // Esto previene el envío tradicional del formulario
            },
        });


        $("#modal-registrar-entrada").on("hidden.bs.modal", function () {
            if (registroSuccessful) {
                Swal.fire({
                    title: 'Éxito',
                    text: 'La entrada fue registrada correctamente.',
                    icon: 'success'
                });
                registroSuccessful = false;
            }
        });
  
        

    });
});
