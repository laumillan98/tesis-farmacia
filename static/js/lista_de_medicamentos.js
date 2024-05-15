$(document).ready(function () {
    let editionSuccessful = false
    var ajaxUrl = $("#miTabla").data("url")
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
            { data: "nombre" },
            { data: "descripcion" },
            { data: "cant_max" },
            { data: "precio" },
            { data: "origen" },
            { data: "restriccion" },
            { data: "clasificacion" },
            {
                data: null,
                orderable: false,
                searchable: false,
                render: function (data, type, row, meta) {  
                    // Verifica si estás en la columna de acciones
                    if (meta.col === 8) {
                        let editButton = `
                            <button id='editar' class='btn btn-sm btn-secondary' data-id='${row.id}' data-toggle='modal' data-target='#modal-lg'>
                                <i class="fas fa-pencil-alt"></i>
                            </button>&nbsp`
                        return editButton
                    }
                    // Puedes retornar diferentes contenidos dependiendo de la columna
                    return data // Retorna los datos originales para otras columnas
                },
            },
        ],
    })


    // Evento de clic en el botón "Editar"
    $('#miTabla').on('click', '#editar', function() {
        let idMedic = $(this).data('id');
        cargarInformacionMedicamento(idMedic);
     });

     function cargarInformacionMedicamento(id) {
        $.ajax({
            url: 'obtenerMedicamento/' + id + '/',
            type: 'GET',
            data: {},
            success: function(response) {
                $('#nombre').val(response.nombre);
                $('#descripcion').val(response.descripcion);
                $('#cant_max').val(response.cant_max);
                $('#precio').val(response.precio);
                $('#origen').val(response.origen ? '1' : '0');
                $('#restriccion').val(response.restriccion_name);
                $('#clasificacion').val(response.clasificacion_name);
                $('#id').val(response.id);

                var $selector = $("#restriccion_selector");
                $selector.empty();
                response.restricciones.forEach(element => {
                    $selector.append($('<option>', {
                    value: element.id_restriccion,
                    text: element.nombre,
                    }))
                });
                $selector.val(response.selected_restriccion_name);    

                var $selector = $("#clasificacion_selector");
                $selector.empty();
                response.clasificaciones.forEach(element => {
                    $selector.append($('<option>', {
                    value: element.id_clasificacion,
                    text: element.nombre,
                    }))
                });
                $selector.val(response.selected_clasificacion_name);   
            },
        })
    }


    function editarMedicamento(form) {
        var formData = $(form).serialize()
    
        // Enviar los datos al servidor usando AJAX
        $.ajax({
          url: "editarMedicamento/",
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
            alert("Ocurrió un error al editar el medicamento")
          },
        })
    }


    $.validator.addMethod("notZero", function(value, element) {
      return parseFloat(value) !== 0; // Verificar que el valor del precio no sea igual a 0
    }, "El valor no puede ser cero");

    $("#edicionMedicamentoForm").validate({
        rules: {
          nombre: {
            required: true,
            minlength: 3,
            pattern: /^[A-Za-z0-9\s]+(?:[A-Za-z][A-Za-z0-9\s]*)?$/
          },
          descripcion: {
            required: true,
            minlength: 5,
            pattern: /^[A-Za-z0-9\s]+(?:[A-Za-z][A-Za-z0-9\s]*)?$/
          },
          cant_max: {
            required: true,
            minlength: 1,
            maxlength: 3,
            digits: true
          },
          precio: {
            required: true,
            minlength: 1,
            maxlength: 5,
            digits: true,
            notZero: true
          },
        },

        messages: {
          nombre: {
            required: "Este campo es obligatorio.",
            minlength: "Por favor, introduce al menos 3 caracteres.",
            pattern: "Por favor introduce al menos una letra, puede contener números."
          },
          descripcion: {
            required: "Este campo es obligatorio.",
            minlength: "Por favor, introduce al menos 5 caracteres.",
            pattern: "Por favor introduce al menos una letra, puede contener números."
          },
          cant_max: {
            required: "Este campo es obligatorio.",
            minlength: "Solo puede contener de 1 a 3 dígitos.",
            maxlength: "Solo puede contener de 1 a 3 dígitos.",
            digits: "No puede contener letras ni símbolos."
          }, 
          precio: {
            required: "Este campo es obligatorio.",
            minlength: "Solo puede contener de 1 a 5 dígitos.",
            maxlength: "Solo puede contener de 1 a 5 dígitos.",
            digits: "No puede contener letras ni símbolos.",
            notZero: "El valor no puede ser cero."
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
            editarMedicamento(form);
            return false // Esto previene el envío tradicional del formulario
        },
    });


    $("#modal-lg").on("hidden.bs.modal", function () {
        if (editionSuccessful) {
            Swal.fire({
                title: 'Éxito',
                text: 'El medicamento fue editado correctamente.',
                icon: 'success'
            });
            editionSuccessful = false;
        }
    })

});
  