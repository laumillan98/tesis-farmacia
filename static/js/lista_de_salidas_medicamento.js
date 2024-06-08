$.getScript("/static/js/datatables.spanish.js", function() {  
    $(document).ready(function () {
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
                { data: "medicamento" },
                { data: "formato" },
                { data: "cantidad" },
                { data: "monto_total" },
                { data: "fecha_movimiento" },
            ],
        });
    });
  });  