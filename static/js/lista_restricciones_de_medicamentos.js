$(document).ready(function() {
    let editionSuccessful = false
    var ajaxUrl = $('#miTabla').data('url');
    var table = $('#miTabla').DataTable({
        ajax: ajaxUrl,
        columns: [
            { data: "index" },
            { data: "id" },
            { data: "nombre" },
            {
                data: null,
                orderable: false,
                searchable: false,
                render: function(data, type, row, meta) {
                    // Verifica si estás en la columna de acciones
                    if (meta.col === 3) { 
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
        cargarInformacionRestriccionMedicamento(idProv);
     });

     function cargarInformacionRestriccionMedicamento(id) {
        $.ajax({
            url: 'obtenerRestriccionMedicamento/' + id + '/',
            type: 'GET',
            data: {},
            success: function(response) {
                $('#restriccion').val(response.name);
                $('#id').val(response.id);
            }
        });
    }


    function editarRestriccionMedicamento(form) {
        var formData = $(form).serialize()
    
        // Enviar los datos al servidor usando AJAX
        $.ajax({
          url: "editarRestriccionMedicamento/",
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
            alert("Ocurrió un error al editar la restricción del medicamento")
          },
        })
    }


    $("#edicionRestriccionMedicamentoForm").validate({
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
            editarRestriccionMedicamento(form);
            return false // Esto previene el envío tradicional del formulario
        },
    });


    $("#modal-lg").on("hidden.bs.modal", function () {
        if (editionSuccessful) {
            Swal.fire({
                title: 'Éxito',
                text: 'La restricción del medicamento fue editada correctamente.',
                icon: 'success'
            });
          editionSuccessful = false;
        }
    })

});