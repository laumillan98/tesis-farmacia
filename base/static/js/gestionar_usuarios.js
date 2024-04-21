(function () {
    const btnEliminarUser = document.querySelectorAll(".btnEliminarUser");

    btnEliminarUser.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const confirmacion = confirm('Seguro que desea eliminar al usuario?');
            if (!confirmacion) {
                e.preventDefault();
            }
        });
    });
})();