$.getScript("/static/js/datatables.spanish.js", function () {
  $(document).ready(function () {
    let editionSuccessful = false
    let map
    let marker

    var ajaxUrl = $("#miTabla").data("url")
    var table = $("#miTabla").DataTable({
      processing: true,
      serverSide: true,
      ajax: {
        url: ajaxUrl,
        type: "GET",
        data: function (d) {
          d.page = d.start / d.length + 1 // Agregar el número de página al request
        },
      },
      columns: [
        { data: "index" },
        { data: "nombre" },
        { data: "prov" },
        { data: "munic" },
        { data: "direccion" },
        { data: "telefono" },
        { data: "tipo" },
        { data: "turno" },
        { data: "usuario_asignado" },
        {
          data: null,
          orderable: false,
          searchable: false,
          render: function (data, type, row, meta) {
            // Verifica si estás en la columna de acciones
            if (meta.col === 9) {
              let editButton = `
                              <button id='editar' class='btn btn-sm btn-success' data-action='editar' data-id='${row.id}' data-toggle='modal' data-target='#modal-lg'>
                                  <i class="fas fa-pencil-alt"></i>
                              </button>&nbsp
                              <button id='verMapa' class='btn btn-sm btn-info' data-lat='${row.latitud}' data-lng='${row.longitud}' data-id='${row.id}'>
                                  <i class="fa-solid fa-location-dot fa-flip"></i>
                              </button>&nbsp
                              <button id='verEstadisticaDeFarmacia' class='btn btn-sm btn-warning' data-id='${row.id}'>
                                <i class="fa-solid fa-chart-simple"></i>
                              </button>`
              return editButton
            }
            // Puedes retornar diferentes contenidos dependiendo de la columna
            return data // Retorna los datos originales para otras columnas
          },
        },
      ],
    })

    // Evento de clic en el botón "Editar"
    $("#miTabla").on("click", "#editar", function () {
      let idFarma = $(this).data("id")
      cargarInformacionFarmacia(idFarma)
    })

    $("#miTabla").on("click", "#verEstadisticaDeFarmacia", function () {
      let idFarma = $(this).data("id")
      window.location.href = "/venta_grafica_farmacia/"+idFarma;
    })

    function cargarInformacionFarmacia(id) {
      $.ajax({
        url: "obtenerFarmacia/" + id + "/",
        type: "GET",
        data: {},
        success: function (response) {
          $("#nombre").val(response.nombre)
          $("#direccion").val(response.direccion)
          $("#telefono").val(response.telefono)
          $("#turno").val(response.turno_name)
          $("#tipo").val(response.tipo_name)
          $("#municipio").val(response.munic_name)
          $("#id").val(response.id)

          var $selector = $("#turno_selector")
          $selector.empty()
          response.turnos.forEach((element) => {
            $selector.append(
              $("<option>", {
                value: element.id_turno,
                text: element.nombre,
              })
            )
          })
          $selector.val(response.selected_turno_name)

          var $selector = $("#tipo_selector")
          $selector.empty()
          response.tipos.forEach((element) => {
            $selector.append(
              $("<option>", {
                value: element.id_tipo,
                text: element.nombre,
              })
            )
          })
          $selector.val(response.selected_tipo_name)

          var $selector = $("#municipio_selector")
          $selector.empty()
          response.municipios.forEach((element) => {
            $selector.append(
              $("<option>", {
                value: element.id_munic,
                text: element.nombre,
              })
            )
          })
          $selector.val(response.selected_munic_name)
        },
      })
    }

    // Evento de clic en el botón "Mapa"
    $("#miTabla").on("click", "#verMapa", function () {
      let lat = $(this).data("lat")
      let lng = $(this).data("lng")
      let id = $(this).data("id")
      console.log(lat)
      console.log(lng)
      if (!validarCoordenadas(lat, lng)) {
        lat = 23.136666666667
        lng = -82.358888888889
      }
      $("#latitud").val(lat)
      $("#longitud").val(lng)
      $("#farmacia_id").val(id)
      $("#mapModal").modal("show")
    })

    $("#mapModal").on("shown.bs.modal", function () {
      let lat = $("#latitud").val()
      let lng = $("#longitud").val()
      console.log(lat)
      if (!map) {
        map = L.map("mapa").setView([lat, lng], 13)
        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        }).addTo(map)
        marker = L.marker([lat, lng], { draggable: true }).addTo(map)
        marker.on("dragend", function (event) {
          let marker = event.target
          let position = marker.getLatLng()
          $("#latitud").val(position.lat)
          $("#longitud").val(position.lng)
          console.log(position.lat)
          console.log(position.lng)
        })
      } else {
        map.setView([lat, lng], 13)
        marker.setLatLng([lat, lng])
      }
      map.invalidateSize()
    })

    $("#guardarUbicacionBtn").click(function () {
      let lat = $("#latitud").val()
      let lng = $("#longitud").val()
      let id = $("#farmacia_id").val()
      guardarUbicacion(id, lat, lng)
    })

    function guardarUbicacion(id, lat, lng) {
      $.ajax({
        url: "editarUbicacionFarmacia/" + id + "/",
        type: "POST",
        headers: { "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val() },
        data: {
          latitud: lat,
          longitud: lng,
        },
        success: function (response) {
          if (response.success === true) {
            Swal.fire({
              title: "Éxito",
              text: "La ubicación de la farmacia fue guardada correctamente.",
              icon: "success",
            })
            $("#mapModal").modal("hide")
            // Actualizar la tabla
            table.ajax.reload()
          } else {
            Swal.fire({
              title: "Error",
              text: "Ocurrió un error al guardar la ubicación de la farmacia.",
              icon: "error",
            })
          }
        },
        error: function (error) {
          Swal.fire({
            title: "Error",
            text: "Ocurrió un error al guardar la ubicación de la farmacia.",
            icon: "error",
          })
        },
      })
    }

    function editarFarmacia(form) {
      var formData = $(form).serialize()

      // Enviar los datos al servidor usando AJAX
      $.ajax({
        url: "editarFarmacia/",
        type: "POST",
        data: formData,
        headers: { "X-CSRFToken": $("input[name=csrfmiddlewaretoken]").val() }, // Incluir el token CSRF
        success: function (response) {
          $("#modal-lg").modal("hide")

          // Mostrar alerta de éxito
          if (response.success === true) {
            editionSuccessful = true
            // Refrescar DataTables
            $("#miTabla").DataTable().ajax.reload()
          }
        },
        error: function (error) {
          alert("Ocurrió un error al editar la farmacia")
        },
      })
    }

    $.validator.addMethod(
      "validPhoneNumber",
      function (value, element) {
        return /^7\d{7}$/.test(value) // Verificar que el número de teléfono comience con 7 y tenga 8 dígitos en total
      },"El número de teléfono debe comenzar con 7 y tener 8 dígitos.")

    $("#edicionFarmaciaForm").validate({
      rules: {
        nombre: {
          required: true,
          minlength: 3,
          pattern: /^[A-Za-z0-9\s]+(?:[A-Za-z][A-Za-z0-9\s]*)?$/,
        },
        direccion: {
          required: true,
          minlength: 5,
          pattern: /^[A-Za-z0-9\s]+(?:[A-Za-z][A-Za-z0-9\s]*)?$/,
        },
        telefono: {
          required: true,
          digits: true,
          validPhoneNumber: true,
        },
      },
      messages: {
        nombre: {
          required: "Este campo es obligatorio.",
          minlength: "Por favor, introduce al menos 3 caracteres.",
          pattern: "Por favor introduce al menos una letra, puede contener números.",
        },
        direccion: {
          required: "Este campo es obligatorio.",
          minlength: "Por favor, introduce al menos 5 caracteres.",
          pattern: "Por favor introduce al menos una letra, puede contener números.",
        },
        telefono: {
          required: "Este campo es obligatorio.",
          digits: "No puede contener letras ni símbolos.",
          validPhoneNumber: "El número de teléfono debe comenzar con 7 y tener 8 dígitos.",
        },
      },
      errorElement: "span",
      errorPlacement: function (error, element) {
        error.addClass("invalid-feedback")
        element.closest(".form-group").append(error)
      },
      highlight: function (element, errorClass, validClass) {
        $(element).addClass("is-invalid")
      },
      unhighlight: function (element, errorClass, validClass) {
        $(element).removeClass("is-invalid")
      },
      submitHandler: function (form) {
        editarFarmacia(form)
        return false // Esto previene el envío tradicional del formulario
      },
    })

    $("#modal-lg").on("hidden.bs.modal", function () {
      if (editionSuccessful) {
        Swal.fire({
          title: "Éxito",
          text: "La farmacia fue editada correctamente.",
          icon: "success",
        })
        editionSuccessful = false
      }
    })

    //funcion para guardar la lat y long
    function validarCoordenadas(latitud, longitud) {
      const lat = parseFloat(latitud)
      const lon = parseFloat(longitud)
      const esLatitudValida = lat >= -90 && lat <= 90
      const esLongitudValida = lon >= -180 && lon <= 180
      return esLatitudValida && esLongitudValida
    }

    $("#ubicarBtn").click(function () {
      let lat = $("#latitud").val()
      let lng = $("#longitud").val()
      map.setView([lat, lng], 13)
      marker.setLatLng([lat, lng])
    })



  });
});
