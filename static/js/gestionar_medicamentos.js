(function () {
    const btnEliminacion = document.querySelectorAll(".btnEliminacion");

    btnEliminacion.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const confirmacion = confirm('Seguro que desea eliminar el medicamento?');
            if (!confirmacion) {
                e.preventDefault();
            }
        });
    });
})();