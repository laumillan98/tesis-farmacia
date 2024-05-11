$(document).ready(function () {
    var ajaxUrl = $("#miTabla").data("url")
    var table = $("#miTabla").DataTable({
        processing: true,
        serverSide: false,  // Cambiar a true si prefieres cargar los datos de forma server-side
        ajax:  ajaxUrl,
        columns: [
            { data: "index" },
            { data: "id" },
            { data: "action_time" },
            { data: "user" },
            { data: "content_type" },
            { data: "object_repr" },
            { data: "action_flag" },
            {
                data: "change_message",
                render: function(data, type, row) {
                    if (data && data.changed && data.changed.fields) {
                        return "Cambios en: " + data.changed.fields.join(", ");
                    } else if (data && data.added) {
                        return "Añadido";
                    } else {
                        return "Sin cambios";
                    }
                }
            }
        ]
    });
});