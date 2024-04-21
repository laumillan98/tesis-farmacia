
  // editarrrrrrrrrrrrrrr

  function abrir_modal_edicion(){
    $('#edicion').load('gestionar_usuarios/editarUsuario/laumillan98/', function(){
        $(this).modal('show');
    })

}

function cerrar_modal_edicion() {
    $('#edicion').modal('hide');
}

function activarBoton(){
    if($('#boton_edicion').prop('disabled')){
        $('#boton_edicion').prop('disabled', false);
    }else{
        $('#boton_edicion').prop('disabled', true);
    }
}


let dataTable;
let dataTableIsInitialized = false;


const dataTableOptions = {
    columnDefs:[
        { className: 'centered', targets:[0, 1, 2, 3, 4, 5, 6, 7] },
        { orderable: false, targets: [6, 7] },
        { searchable: false, targets: [0, 6, 7] }
    ],

    pageLength: 7,
    destroy: true

};


const initDataTable = async () => {
    if(dataTableIsInitialized){
        dataTable.destroy();
    }

    await listaDeFarmacias();

    dataTable = $("#datatable-farmacias").DataTable(dataTableOptions);

    dataTableIsInitialized = true;
};


const listaDeFarmacias = async () => {
    try{  
        const response = await fetch('http://127.0.0.1:8000/lista_de_farmacias/');
        const data = await response.json();

        console.log(response)

        let content = ``;
        
        data.farmacias.forEach((farmacia, index) => {

            let buttonContent = farmacia.is_active 
            ? "<button id='editar' class='btn btn-sm btn-secondary' data-action='editar'><i class='fa-solid fa-pencil'></i></button>&nbsp<button id='softdelete' class='btn btn-sm btn-danger' data-id='"+ farmacia.nombre +"'><i class='fa-solid fa-trash-can'></i></button>"
            : "<button id='activar' class='btn btn-sm btn-secondary' data-id='"+ farmacia.nombre +"' data-action='activar'><i class='fas fa-trash-restore-alt'></i></button>";

            content += `
                <tr>
                    <td>${index + 1}</td>
                    <td>${farmacia.nombre}</td>
                    <td>${farmacia.id_prov}</td>
                    <td>${farmacia.id_munic}</td>
                    <td>${farmacia.direccion}</td>
                    <td>${farmacia.telefono}</td>
                    <td>${farmacia.id_tipo}</td>
                    <td>${farmacia.id_turno}</td>
                    <td>${farmacia.is_active == true 
                        ? "<i class='fa-solid fa-check' style='color: green'></i>" 
                        : "<i class='fa-solid fa-xmark' style='color: red'></i>"}</td>
                    <td>${buttonContent}</td>   
                </tr>
            `;    
        }); 
        tableBody_farmacias.innerHTML = content;
    } catch (ex) {
        alert(ex);
    }
};

window.addEventListener("load", async () => {
    await initDataTable();


    // Evento de clic en el botón "Eliminar"
    $('#datatable-farmacias').on('click', '#softdelete', function() {
        var nombreFarmacia = $(this).data('id'); 
        
        //Ejecuta el plugin (Sweet Alert) para confirmar la eliminación del usuario 
        Swal.fire({
            title: "¿Está seguro que desea eliminar la farmacia " + nombreFarmacia + "?",
            icon: "question",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Aceptar"
          }).then((result) => {
            if (result.isConfirmed) {
                var id = $(this).data('id');
                deleteFarma(id, $(this).closest('tr'));  
            }
          });
    });


    // Función AJAX para eliminar un usuario
    function deleteFarma(id, row) {
        $.ajax({
            url: 'eliminarFarmacia/' + id + '/',
            type: 'GET',
            data: {},
            success: function(response) {
                if (response.status == 'success') {
                    //Actualiza el estado del usuario eliminado
                    listaDeFarmacias();
                    Swal.fire({
                        title: id + " ha sido eliminada satisfactoriamente!",
                        icon: "success",
                        confirmButtonColor: "#3085d6",
                        confirmButtonText: "Aceptar"
                    });
                } else {
                    // Maneja el error
                    alert('No se pudo eliminar el elemento.');
                }
            }
        });
    }


    // Evento de clic en el botón "Activar"
    $('#datatable-farmacias').on('click', '#activar', function() {
        var nombreFarmacia = $(this).data('id');

        //Ejecuta el plugin (Sweet Alert) para confirmar la activación del usuario 
        Swal.fire({
            title: "¿Está seguro que desea activar a " + nombreFarmacia + "?",
            icon: "question",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Aceptar"
          }).then((result) => {
            if (result.isConfirmed) {
                var id = $(this).data('id');
                activarFarma(id, $(this).closest('tr')); 
              Swal.fire({
                title: "¡" + nombreFarmacia + " ha sido activado satisfactoriamente!",
                icon: "success",
                confirmButtonColor: "#3085d6",
                confirmButtonText: "Aceptar"
              });
            }
          });
        
    });

    // Función AJAX para "Activar un usuario"
    function activarFarma(id, row) {
        $.ajax({
            url: 'activarFarmacia/' + id + '/',
            type: 'GET',
            data: {
                'username': id,
                'csrfmiddlewaretoken': '{{ csrf_token }}' // Token CSRF de Django
            },
            success: function(response) {
                if (response.status == 'success') {
                    // Actualiza el estado del usuario activado
                    listaDeFarmacias();
                } else {
                    // Maneja el error
                    alert('No se pudo activar el usuario.');
                }
            }
        });
    }


    // Evento de clic en el botón "Editar"
    $('#datatable-farmacias').on('click', '#editar', function() {
        var nombreUsuario = $(this).data('id'); 
        editarFarma(nombreUsuario, $(this).closest('tr'));
    });


    // Función AJAX para "Editar un usuario"
    function editarFarma(id, row) {
        abrir_modal_edicion();
    }
});