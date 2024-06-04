$.getScript("/static/js/datatables.spanish.js", function() { 
  $(document).ready(function () {
      let editionSuccessful = false
      var ajaxUrl = $("#miTabla").data("url")
      var table = $("#miTabla").DataTable({
        ajax: ajaxUrl,
        columns: [
          { data: "index" },
          { data: "nombre" },
          { data: "provincia" },
          {
            data: null,
            orderable: false,
            searchable: false,
            render: function (data, type, row, meta) {
              // Verifica si estás en la columna de acciones
              if (meta.col === 3) {
                  let editButton = `
                      <button id='editar' class='btn btn-sm btn-success' data-id='${row.id}' data-toggle='modal' data-target='#modal-lg'>
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
      $("#miTabla").on("click", "#editar", function () {
        let idMunic = $(this).data("id")
        cargarInformacionMunicipio(idMunic)
      })
    
      
      function cargarInformacionMunicipio(id) {
        $.ajax({
          url: "obtenerMunicipio/" + id + "/",
          type: "GET",
          data: {},
          success: function (response) {
            $("#municipio").val(response.name)
            $("#provincia").val(response.prov_name)
            $("#id").val(response.id)
            var $selector = $("#provicia_selector");
            $selector.empty();
    
            response.provincias.forEach(element => {
              $selector.append($('<option>', {
                value: element.id_prov,
                text: element.nombre,
              }))
            });
    
            $selector.val(response.selected_prov_name);
          },
        })
      }
    

      function editarMunicipio(form) {
          var formData = $(form).serialize()
      
          // Enviar los datos al servidor usando AJAX
          $.ajax({
              url: "editarMunicipio/",
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
                alert("Ocurrió un error al editar el municipio")
              },
          })
      }


      $("#edicionMunicipioForm").validate({
          rules: {
            nombre: {
              required: true,
              minlength: 3,
              pattern: /^[A-Za-z0-9\s]+(?:[A-Za-z][A-Za-z0-9\s]*)?$/
            },
          },
          messages: {
            nombre: {
              required: "Este campo es obligatorio.",
              minlength: "Por favor, introduce al menos 3 caracteres.",
              pattern: "Por favor introduce al menos una letra, puede contener números."
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
            editarMunicipio(form);
            return false // Esto previene el envío tradicional del formulario
          },
      });

    
      $("#modal-lg").on("hidden.bs.modal", function () {
        if (editionSuccessful) {
            Swal.fire({
                title: 'Éxito',
                text: 'El municipio fue editado correctamente.',
                icon: 'success'
            });
          editionSuccessful = false;
        }
      });


      // Funcion para registrar un nuevo Municipio
      function registrarMunicipio(form) {
        var formData = $(form).serialize();
        $.ajax({
            url: "registrarMunicipio/",
            type: "POST",
            data: formData,
            headers: { "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val() },
            success: function(response) {
                $("#modal-registrar-municipio").modal("hide");
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
                            text: 'Ocurrió un error al registrar el municipio1.',
                            icon: 'error'
                        });
                    }
                }
            },
            error: function() {
                Swal.fire({
                    title: 'Error',
                    text: 'Ocurrió un error al registrar el municipio2.',
                    icon: 'error'
                });
            },
        });
    }

    $("#registroMunicipioForm").validate({
        rules: {
            nombre: {
                required: true,
                minlength: 3,
                maxlength: 25,
                pattern: /^[A-Za-záéíóúÁÉÍÓÚüÜ\s]+$/
            },
        },
        messages: {
            nombre: {
                required: "Este campo es obligatorio.",
                minlength: "Por favor, introduce al menos 3 caracteres.",
                maxlength: "No puede contener más de 25 caracteres.",
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
            registrarMunicipio(form);
            return false;
        },
    });

    $("#modal-registrar-municipio").on("hidden.bs.modal", function () {
        if (registroSuccessful) {
            Swal.fire({
                title: 'Éxito',
                text: 'El municipio fue registrado correctamente.',
                icon: 'success'
            });
            registroSuccessful = false;
        }
        // Limpiar el formulario del modal de registro
        $('#registroMunicipioForm')[0].reset();
        $('#registroMunicipioForm').find('.is-invalid').removeClass('is-invalid');
        $('#registroMunicipioForm').find('.invalid-feedback').remove();
    });

    $('#registrarMunicipioButton').on('click', function() {
      // Llenar el select de provincia cuando se abre el modal de registro
      cargarProvincias();
      $('#modal-registrar-municipio').modal('show');
    });

    function cargarProvincias() {
        $.ajax({
            url: 'obtenerProvMunicipio/',
            type: 'GET',
            success: function(response) {
                var $selector = $('#provinciaRegistro');
                $selector.empty();
                response.provincias.forEach(element => {
                    $selector.append($('<option>', {
                        value: element.id_prov,
                        text: element.nombre,
                    }));
                });
            },
            error: function() {
                Swal.fire({
                    title: 'Error',
                    text: 'No se pudieron cargar las provincias.',
                    icon: 'error'
                });
            }
        });
    } 


  });
});  
  