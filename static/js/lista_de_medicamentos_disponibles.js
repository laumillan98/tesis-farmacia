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
            { data: "nombre" },
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
                  <button id='mostrar' class='btn btn-sm btn-info' data-id='${row.id}' data-toggle='modal' data-target='#modaldesc-lg'>
                      <i class="fa-solid fa-eye"></i>
                  </button>`;
                  return mostrarButton;
              }
            },
            {
              data: null,
              orderable: false,
              searchable: false,
              render: function (data, type, row, meta) {
                  let exportButton = `
                  <button id='exportar' class='btn btn-sm btn-primary' data-id='${row.id}' data-toggle='modal' data-target='#modal-lg'>
                      <i class="fa-solid fa-file-export"></i>
                  </button>`;
                  return exportButton;
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
              $('#descripcionMostrar').text(response.description);
              $('#id').val(response.id);
              $('#modaldesc-lg').modal('show'); 
          },
      })
    }


    // Evento de clic en el botón "Exportar"
    $('#miTabla').on('click', '#exportar', function() {
        let idMedic = $(this).data('id');
        exportarMedicamento(idMedic);
    });

    function exportarMedicamento(id) {
        $.ajax({
            url: 'exportarMedicamento/' + id + '/',
            type: 'POST',
            data: {},
            headers: { 'X-CSRFToken': '{{ csrf_token }}' },  // Añadir CSRF token
            success: function(response) {
                if (response.status === 'success') {
                    Swal.fire({
                        title: 'Exportado',
                        text: 'El medicamento ha sido exportado a tu farmacia con éxito.',
                        icon: 'success',
                        confirmButtonText: 'Aceptar'
                    });
                } else {
                    Swal.fire({
                        title: 'Error',
                        text: response.message,
                        icon: 'error',
                        confirmButtonText: 'Aceptar'
                    });
                }
            },
            error: function(response) {
                Swal.fire({
                    title: 'Error',
                    text: 'No se pudo exportar el medicamento. Inténtalo nuevamente.',
                    icon: 'error',
                    confirmButtonText: 'Aceptar'
                });
            }
        });
    }


});
  