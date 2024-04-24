$(document).ready(function () {

    $('.incrementBtn').click(function (e) {
        e.preventDefault();

        var medicamento = $(this).closest('.existenciaData').find('.uuid-medicamento').val();
        var quantity = $(this).closest('.existenciaData').find('.input-qty').val();
        var new_value = parseInt(quantity) + 1;
        $(this).closest('.existenciaData').find('.input-qty').val(new_value);
        saveQuantity(new_value, medicamento);
    });

    $('.decrementBtn').click(function (e) {
        e.preventDefault();

        var medicamento = $(this).closest('.existenciaData').find('.uuid-medicamento').val();
        var quantity = $(this).closest('.existenciaData').find('.input-qty').val();
        var new_value = parseInt(quantity) - 1;
        if (new_value >= 0) {
            $(this).closest('.existenciaData').find('.input-qty').val(new_value);
            saveQuantity(new_value, medicamento);
        }
    });

    function saveQuantity(arg, arg2) {
        var farmacia = $('#idFarmacia').val();
        var token = $('input[name=csrfmiddlewaretoken]').val();

        $.ajax({
            type: "POST",
            url: "/actualizarCantidad",
            data: {
                'farmacia':farmacia,
                'medicamento':arg2,
                'cantidad':arg,
                csrfmiddlewaretoken: token
            },
            success: function (response) {
                console.log(response.status);
            }
        });
    };

});