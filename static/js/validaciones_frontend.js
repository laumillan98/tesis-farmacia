const edicionUsuarioForm = document.getElementById('edicionUsuarioForm');
const inputs = document.querySelectorAll('#edicionUsuarioForm input');


const expresiones = {
    usuario: /^[a-zA-Z0-9\_\-]{4,16}$/,
    nombre: /^[A-Za-zÁ ]{3,50}$/,
    apellido: /^[A-Za-zÁ ]{3,50}$/,
    correo: /^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$/,
    telefono: /^\d{8}$/,
}

const validarEdicionUsuarioForm = (e) => {
    switch (e.target.name) {
        case "first_name":
            if(expresiones.nombre.test(e.target.value)){
                
            } else {
                document.getElementById('grupo_nombre').classList.add('.')
            }
        break;
    }
}

inputs.forEach((input) => { 
    // para cuando se levante la tecla compruebe
    input.addEventListener('keyup', validarEdicionUsuarioForm);
    // para cuando se de un click fuera compruebe
    input.addEventListener('blur', validarEdicionUsuarioForm);
});

edicionUsuarioForm.addEventListener('submit', (e) => {
    e.preventDefault();
});