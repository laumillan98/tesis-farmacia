
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
    paging: true,
    pageLength: 7,
    //destroy: true

};


const initDataTable = async () => {
    if(dataTableIsInitialized){
        dataTable.destroy();
    }

    await listaDeUsuarios();

    dataTable = $("#datatable-usuarios").DataTable(dataTableOptions);

    dataTableIsInitialized = true;
};


const listaDeUsuarios = async () => {
    try{  
        const response = await fetch('http://127.0.0.1:8000/lista_de_usuarios/');
        const data = await response.json();

        console.log(response)

        let content = ``;
        data.usuarios.forEach((usuario, index) => {

            let buttonContent2 = usuario.is_active 
            ? "<button id='editar' class='btn btn-sm btn-secondary' data-action='editar'><i class='fas fa-pencil-alt'></i></button>&nbsp<button id='softdelete' class='btn btn-sm btn-danger' data-id='"+ usuario.username +"'><i class='fa-solid fa-trash-can'></i></button>"
            : "<button id='activar' class='btn btn-sm btn-secondary' data-id='"+ usuario.username +"' data-action='activar'><i class='fas fa-trash-restore-alt'></i></button>";

            let buttonContent1 = usuario.is_superuser 
            ? "<button id='editar' class='btn btn-sm btn-secondary' data-action='editar'><i class='fas fa-pencil-alt'></i></button>"
            : ""+ buttonContent2 +"";

            content += `
                <tr>
                    <td>${index + 1}</td>
                    <td>${usuario.first_name}</td>
                    <td>${usuario.last_name}</td>
                    <td>${usuario.username}</td>
                    <td>${usuario.email}</td>
                    <td>${usuario.first_group}</td>
                    <td>${usuario.is_active == true 
                        ? "<i class='fa-solid fa-check' style='color: green'></i>" 
                        : "<i class='fa-solid fa-xmark' style='color: red'></i>"}</td>
                    <td>${buttonContent1}</td>      
                </tr>
            `;    
        }); 
        tableBody_usuarios.innerHTML = content;
    } catch (ex) {
        alert(ex);
    }
};

window.addEventListener("load", async () => {
    await initDataTable();


    // Evento de clic en el botón "Eliminar"
    $('#datatable-usuarios').on('click', '#softdelete', function() {
        var nombreUsuario = $(this).data('id'); 
        
        //Ejecuta el plugin (Sweet Alert) para confirmar la eliminación del usuario 
        Swal.fire({
            title: "¿Está seguro que desea eliminar a " + nombreUsuario + "?",
            icon: "question",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Aceptar"
          }).then((result) => {
            if (result.isConfirmed) {
                var id = $(this).data('id');
                deleteUser(id, $(this).closest('tr'));  
            }
          });
    });


    // Función AJAX para eliminar un usuario
    function deleteUser(id, row) {
        $.ajax({
            url: 'eliminarUsuario/' + id + '/',
            type: 'GET',
            data: {},
            success: function(response) {
                if (response.status == 'success') {
                    //Actualiza el estado del usuario eliminado
                    listaDeUsuarios();
                    Swal.fire({
                        title: id + " ha sido eliminado satisfactoriamente!",
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
    $('#datatable-usuarios').on('click', '#activar', function() {
        var nombreUsuario = $(this).data('id');

        //Ejecuta el plugin (Sweet Alert) para confirmar la activación del usuario 
        Swal.fire({
            title: "¿Está seguro que desea activar a " + nombreUsuario + "?",
            icon: "question",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Aceptar"
          }).then((result) => {
            if (result.isConfirmed) {
                var id = $(this).data('id');
                activarUsuario(id, $(this).closest('tr')); 
              Swal.fire({
                title: "¡" + nombreUsuario + " ha sido activado satisfactoriamente!",
                icon: "success",
                confirmButtonColor: "#3085d6",
                confirmButtonText: "Aceptar"
              });
            }
          });
        
    });

    // Función AJAX para "Activar un usuario"
    function activarUsuario(id, row) {
        $.ajax({
            url: 'activarUsuario/' + id + '/',
            type: 'GET',
            data: {
                'username': id,
                'csrfmiddlewaretoken': '{{ csrf_token }}' // Token CSRF de Django
            },
            success: function(response) {
                if (response.status == 'success') {
                    // Actualiza el estado del usuario activado
                    listaDeUsuarios();
                } else {
                    // Maneja el error
                    alert('No se pudo activar el usuario.');
                }
            }
        });
    }


    // Evento de clic en el botón "Editar"
    $('#datatable-usuarios').on('click', '#editar', function() {
        var nombreUsuario = $(this).data('id'); 
        editarUsuario(nombreUsuario, $(this).closest('tr'));
    });


    // Función AJAX para "Editar un usuario"
    function editarUsuario(id, row) {
        abrir_modal_edicion();
    }
});