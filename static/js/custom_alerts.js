document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");
    form.addEventListener("submit", function(event) {
      event.preventDefault();
      Swal.fire({
        position: "middle",
        icon: "success",
        title: "Tu perfil ha sido actualizado",
        showConfirmButton: false,
        timer: 1500
      }).then(function() {
        form.submit();
      });
    });
});