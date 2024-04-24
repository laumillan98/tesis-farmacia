let dataTable;
let dataTableIsInitialized = false;


const dataTableOptions = {
    columnDefs:[
        { className: 'centered', targets:[0, 1, 2, 3, 4, 5, 6, 7, 8, 9] },
        { orderable: false, targets: [8, 9] },
        { searchable: false, targets: [0, 8, 9] }
    ],

    pageLength: 7,
    destroy: true

};


const initDataTable = async () => {
    if(dataTableIsInitialized){
        dataTable.destroy();
    }

    await listaDeMunicipios();

    dataTable = $("#datatable-municipios").DataTable(dataTableOptions);

    dataTableIsInitialized = true;
};


const listaDeMunicipios = async () => {
    try{  
        const response = await fetch('http://127.0.0.1:8000/lista_de_municipios/');
        const data = await response.json();

        console.log(response)

        let content = ``;
        
        data.municipios.forEach((municipio, index) => {

            let buttonContent = municipio.is_active 
            ? "<button id='editar' class='btn btn-sm btn-secondary' data-action='editar'><i class='fa-solid fa-pencil'></i></button>&nbsp<button id='softdelete' class='btn btn-sm btn-danger' data-id='"+ municipio.id_munic +"' data-nombre='"+ municipio.nombre +"'><i class='fa-solid fa-trash-can'></i></button>"
            : "<button id='activar' class='btn btn-sm btn-secondary' data-id='"+ municipio.id_munic +"' data-nombre='"+ municipio.nombre +"' data-action='activar'><i class='fas fa-trash-restore-alt'></i></button>";

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
        tableBody_municipios.innerHTML = content;
    } catch (ex) {
        alert(ex);
    }
};

window.addEventListener("load", async () => {
    await initDataTable();


    // Evento de clic en el botón "Eliminar"
    $('#datatable-municipios').on('click', '#softdelete', function() {
        var nombreMunic = $(this).data('nombre')
        
        //Ejecuta el plugin (Sweet Alert) para confirmar la eliminación del municipio 
        Swal.fire({
            title: "¿Está seguro que desea eliminar la farmacia " + nombreFarma + "?",
            icon: "question",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Aceptar"
          }).then((result) => {
            if (result.isConfirmed) {
                var id = $(this).data('id');
                deleteMunic(id, nombreMunic, $(this).closest('tr'));  
            }
          });
    });


    // Función AJAX para eliminar un municipio
    function deleteMunic(id, nombreMunic, row) {
        $.ajax({
            url: 'eliminarMunicipio/' + id + '/',
            type: 'GET',
            data: {},
            success: function(response) {
                if (response.status == 'success') {
                    //Actualiza el estado del usuario eliminado
                    listaDeMunicipios();
                    Swal.fire({
                        title: "¡" + nombreMunic + " ha sido eliminado satisfactoriamente!",
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
    $('#datatable-municipios').on('click', '#activar', function() {
        var nombreMunic = $(this).data('nombre');

        //Ejecuta el plugin (Sweet Alert) para confirmar la activación del municipio 
        Swal.fire({
            title: "¿Está seguro que desea activar a " + nombreMunic + "?",
            icon: "question",
            showCancelButton: true,
            confirmButtonColor: "#3085d6",
            cancelButtonColor: "#d33",
            confirmButtonText: "Aceptar"
          }).then((result) => {
            if (result.isConfirmed) {
                var id = $(this).data('id');
                activarMunic(id, $(this).closest('tr')); 
              Swal.fire({
                title: "¡" + nombreMunic + " ha sido activado satisfactoriamente!",
                icon: "success",
                confirmButtonColor: "#3085d6",
                confirmButtonText: "Aceptar"
              });
            }
          });
        
    });

    // Función AJAX para "Activar un municipio"
    function activarMunic(id, row) {
        $.ajax({
            url: 'activarMunicipio/' + id + '/',
            type: 'GET',
            data: {
                'id_munic': id,
                'csrfmiddlewaretoken': '{{ csrf_token }}' // Token CSRF de Django
            },
            success: function(response) {
                if (response.status == 'success') {
                    // Actualiza el estado del municipio activado
                    listaDeFarmacias();
                } else {
                    // Maneja el error
                    alert('No se pudo activar el municipio.');
                }
            }
        });
    }

});