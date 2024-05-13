$(document).ready(function () {
    let editionSuccessful = false
    var ajaxUrl = $("#miTabla").data("url")
    var table = $("#miTabla").DataTable({
        ajax: ajaxUrl,
        columns: [
            { data: "index" },
            { data: "nombre" },
            { data: "descripcion" },
            { data: "cant_max" },
            { data: "precio" },
            { data: "origen" },
            { data: "restriccion" },
            { data: "existencia" },
            {
            data: null,
            orderable: false,
            searchable: false,
            render: function (data, type, row, meta) {  ////////////cambiar boton editar por boton de EXISTENCIASSSSS
                // Verifica si estás en la columna de acciones
                if (meta.col === 8) {
                    let editButton = `
                        <button id='editar' class='btn btn-sm btn-secondary' data-id='${row.id}' data-toggle='modal' data-target='#modal-lg'>
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
})
  