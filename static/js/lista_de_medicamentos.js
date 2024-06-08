$.getScript("/static/js/datatables.spanish.js", function() {  
  $(document).ready(function () {
    $('#descriptionEdit').summernote(
      {
        toolbar: [
          // Aquí incluyes solo los grupos de botones que deseas habilitar
          ['style', ['bold', 'italic', 'underline', 'clear']],
          ['font', ['strikethrough', 'superscript', 'subscript']],
          ['fontsize', ['fontsize']],
          ['color', ['color']],
          ['para', ['ul', 'ol', 'paragraph']],
          ['height', ['height']]
          // No incluir ['insert', ['link', 'picture', 'video']],
          // No incluir ['view', ['fullscreen', 'codeview']],
          // No incluir ['help', ['help']]
        ],
        // Otras opciones de configuración...
      }
    );
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
              { data: "nombre" },
              { data: "formato" },
              { data: "cant_max" },
              { data: "precio_unidad" },
              { data: "origen" },
              { data: "restriccion" },
              { data: "clasificacion" },
              {
                data: null,
                orderable: false,
                searchable: false,
                render: function (data, type, row, meta) {
                    let mostrarButton = `
                    <button id='mostrar' class='btn btn-sm btn-info mr-2' data-id='${row.id}' data-toggle='modal' data-target='#modaldesc-lg'>
                        <i class="fa-solid fa-eye"></i>
                    </button>`;
                    let reacButton = `
                    <button id='mostrarReac' class='btn btn-sm btn-warning' data-id='${row.id}' data-toggle='modal' data-target='#modalreac-lg'>
                        <i class="fa-solid fa-triangle-exclamation fa-beat"></i>
                    </button>`;
                    return mostrarButton + reacButton;
                }
              },
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


      // Evento de clic en el botón "Mostrar"
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
                $('#descripcionMostrar').html(response.description);
                $('#id').val(response.id);
                $('#modaldesc-lg').modal('show'); 
            },
        })
      }


      // Evento de clic en el botón "Reacciones"
      $('#miTabla').on('click', '#mostrarReac', function() {
        let idMedic = $(this).data('id');
        cargarReaccionesMedicamento(idMedic);
      });

      function cargarReaccionesMedicamento(id) {
        $.ajax({
            url: 'obtenerReacciones/' + id + '/',
            type: 'GET',
            data: {},
            success: function(response) {
                $('#reaccionesMostrar').html(response.reacciones);
                $('#id').val(response.id);
                $('#modalreac-lg').modal('show'); 
            },
        })
      }


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
                  //console.log('Respuesta del servidor:', response);
                  $('#nombre').val(response.nombre);
                  $('#modal-lg').modal('show');
                  $('#descriptionEdit').summernote('code', response.description);
                  $('#reaccionesEdit').summernote('code', response.reacciones);
                  $('#cant_max').val(response.cant_max);
                  $('#precio_unidad').val(response.precio_unidad);

                  if (response.origen) {
                    $('#origen').prop('checked', true);
                  } else {
                    $('#origen').prop('checked', false);
                  }

                  $('#restriccion').val(response.restriccion_name);
                  $('#clasificacion').val(response.clasificacion_name);
                  $('#formato').val(response.formato_name);
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
                  
                  var $selector = $("#formato_selector");
                  $selector.empty();
                  response.formatos.forEach(element => {
                      $selector.append($('<option>', {
                      value: element.id_formato,
                      text: element.nombre,
                      }))
                  });
                  $selector.val(response.selected_formato_name);
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
              pattern: /^[A-Za-zÁáÉéÍíÓóÚúÜüÑñ\s]+$/
            },
            description: {
              required: true,
              minlength: 5,
              pattern: /^[A-Za-z0-9\s.,;:"'ÁáÉéÍíÓóÚúÜüÑñ()]+$/u
            },
            reacciones: {
              required: true,
              minlength: 5,
              pattern: /^[A-Za-z0-9\s.,;:"'ÁáÉéÍíÓóÚúÜüÑñ()]+$/u
            },
            cant_max: {
              required: true,
              minlength: 1,
              maxlength: 3,
              digits: true
            },
            precio_unidad: {
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
              pattern: "No puede contener números ni símbolos."
            },
            description: {
              required: "Este campo es obligatorio.",
              minlength: "Por favor, introduce al menos 5 caracteres.",
              pattern: "Por favor introduce al menos una letra, puede contener números."
            },
            reacciones: {
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
            precio_unidad: {
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
      });


  });
});  