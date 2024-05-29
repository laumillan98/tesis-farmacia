$(document).ready(function () {
    var ajaxUrl = $("#miTabla").data("url");
    var table = $("#miTabla").DataTable({
        processing: true,
        serverSide: true,
        ajax: {
            'url': ajaxUrl,
            'type': "GET",
            "data": function(d) {
                d.page = (d.start / d.length) + 1;
            },
            "dataSrc": function (json) {
                if (json.error) {
                    console.error(json.error);
                    alert('Error: ' + json.error);
                    return [];
                }
                return json.data;
            }
        },
        columns: [
            { data: "index" },
            { data: "action_time" },
            { data: "user" },
            { data: "ip_address" },
            { data: "content_type" },
            { data: "object_repr" },
            { data: "action_flag" }, 
            {
                data: "change_message",
                render: function(data, type, row) {
                    if (data) {
                        return data;
                    } else {
                        return "Sin cambios";
                    }
                }
            }
        ]
    });
});