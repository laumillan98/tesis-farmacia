$(document).ready(function() {
    let editionSuccessful = false
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
            { data: "nombre" },
            { data: "prov" },
            { data: "munic" },
            { data: "direccion" },
            { data: "telefono" },
            { data: "tipo",  orderable: false, },
            { data: "turno",  orderable: false, },
            { data: "usuario_asignado",  orderable: false,},
            {
                data: null,
                orderable: false,
                searchable: false,
                render: function (data, type, row, meta) {
                    // Verifica si estás en la columna de acciones
                    if (meta.col === 9) { 
                        let editButton = `
                            <button id='editar' class='btn btn-sm btn-success' data-action='editar' data-id='${row.id}' data-toggle='modal' data-target='#modal-lg'>
                                <i class="fas fa-pencil-alt"></i>
                            </button>&nbsp`
                        return editButton 
                    }
                    // Puedes retornar diferentes contenidos dependiendo de la columna
                    return data; // Retorna los datos originales para otras columnas
                },
            },
        ],
    })

    
    // Evento de clic en el botón "Editar"
    $('#miTabla').on('click', '#editar', function() {
        let idFarma = $(this).data('id');
        cargarInformacionFarmacia(idFarma);
     });

     function cargarInformacionFarmacia(id) {
        $.ajax({
            url: 'obtenerFarmacia/' + id + '/',
            type: 'GET',
            data: {},
            success: function(response) {
                $('#nombre').val(response.nombre);
                $('#direccion').val(response.direccion);
                $('#telefono').val(response.telefono);
                $('#turno').val(response.turno_name);
                $('#tipo').val(response.tipo_name);
                $('#municipio').val(response.munic_name);
                $('#id').val(response.id);

                var $selector = $("#turno_selector");
                $selector.empty();
                response.turnos.forEach(element => {
                    $selector.append($('<option>', {
                    value: element.id_turno,
                    text: element.nombre,
                    }))
                });
                $selector.val(response.selected_turno_name);    

                var $selector = $("#tipo_selector");
                $selector.empty();
                response.tipos.forEach(element => {
                    $selector.append($('<option>', {
                    value: element.id_tipo,
                    text: element.nombre,
                    }))
                });
                $selector.val(response.selected_tipo_name); 

                var $selector = $("#municipio_selector");
                $selector.empty();
                response.municipios.forEach(element => {
                    $selector.append($('<option>', {
                    value: element.id_munic,
                    text: element.nombre,
                    }))
                });
                $selector.val(response.selected_munic_name); 
            },
        })
    }


    function editarFarmacia(form) {
        var formData = $(form).serialize()
    
        // Enviar los datos al servidor usando AJAX
        $.ajax({
          url: "editarFarmacia/",
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
            alert("Ocurrió un error al editar la farmacia")
          },
        })
    }


    $("#edicionFarmaciaForm").validate({
        rules: {
          nombre: {
            required: true,
            minlength: 3,
            pattern: /^[A-Za-z0-9\s]+(?:[A-Za-z][A-Za-z0-9\s]*)?$/
          },
          direccion: {
            required: true,
            minlength: 5,
            pattern: /^[A-Za-z0-9\s]+(?:[A-Za-z][A-Za-z0-9\s]*)?$/
          },
          telefono: {
            required: true,
            minlength: 8,
            maxlength: 8,
            digits: true
          },
        },

        messages: {
          nombre: {
            required: "Este campo es obligatorio.",
            minlength: "Por favor, introduce al menos 3 caracteres.",
            pattern: "Por favor introduce al menos una letra, puede contener números."
          },
          direccion: {
            required: "Este campo es obligatorio.",
            minlength: "Por favor, introduce al menos 5 caracteres.",
            pattern: "Por favor introduce al menos una letra, puede contener números."
          },
          telefono: {
            required: "Este campo es obligatorio.",
            minlength: "Solo puede contener 8 dígitos.",
            maxlength: "Solo puede contener 8 dígitos.",
            digits: "No puede contener letras ni símbolos."
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
            editarFarmacia(form);
            return false // Esto previene el envío tradicional del formulario
        },
    });


    $("#modal-lg").on("hidden.bs.modal", function () {
        if (editionSuccessful) {
            Swal.fire({
                title: 'Éxito',
                text: 'La farmacia fue editada correctamente.',
                icon: 'success'
            });
            editionSuccessful = false;
        }
    })

});