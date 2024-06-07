$.getScript("/static/js/datatables.spanish.js", function() {
    $(document).ready(function () {
        let guardarSuccessful = false;
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
                { data: "precio" },
                {
                    data: "existencia",
                    render: function(data, type, row, meta) {
                        return `<input type="number" class="form-control ventas-input" data-id="${row.id}" data-existencia="${row.existencia}" max="${row.existencia}" min="0" value="0">`;
                    }
                },
            ],
        });

        $('#guardarCierre').on('click', function() {
            let ventas = [];
            $('.ventas-input').each(function() {
                let cantidad = parseInt($(this).val());
                if (cantidad > 0) {
                    let existencia = parseInt($(this).data('existencia'));
                    if (cantidad > existencia) {
                        Swal.fire({
                            title: 'Error',
                            text: 'La cantidad de ventas no puede ser mayor a la existencia',
                            icon: 'error'
                        });
                        return false;
                    }
                    ventas.push({
                        id: $(this).data('id'),
                        cantidad: cantidad
                    });
                }
            });

            if (ventas.length > 0) {
                $.ajax({
                    url: "{% url 'guardar_ventas' %}",
                    type: "POST",
                    data: JSON.stringify(ventas),
                    contentType: "application/json",
                    headers: { "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val() },
                    success: function (response) {
                        if (response.success === true) {
                            Swal.fire({
                                title: 'Éxito',
                                text: 'Las ventas fueron registradas correctamente.',
                                icon: 'success'
                            }).then(function() {
                                window.location.href = "{% url 'gestionar_salidas_medicamento' %}";
                            });
                        } else {
                            Swal.fire({
                                title: 'Error',
                                text: 'Ocurrió un error al registrar las ventas',
                                icon: 'error'
                            });
                        }
                    },
                    error: function (error) {
                        Swal.fire({
                            title: 'Error',
                            text: 'Ocurrió un error al registrar las ventas',
                            icon: 'error'
                        });
                    },
                });
            } else {
                Swal.fire({
                    title: 'Error',
                    text: 'No hay ventas para registrar',
                    icon: 'error'
                });
            }
        });
    });
});
