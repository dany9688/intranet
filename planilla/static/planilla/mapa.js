var socketServicios = new WebSocket('wss://' + window.location.host + '/ws/servicios/');
var socket = new WebSocket('wss://' + window.location.host + '/ws/location/');

    // Inicializa el mapa y el geocodificador
    var map;
    var geocoder;
    var marker;
    var marker1;
    var markers = [];
    var hidrantesMarkers = [];  // Array para almacenar los marcadores de hidrantes
    var hidrantesLayer;  // Capa para hidrantes
    var cuartelesMarkers = [];  // Array para almacenar los marcadores de cuarteles
    var cuartelesLayer;  // Capa para cuarteles
    var infoWindow; // Ventana emergente para mostrar información
    var staticUrl = "/static/planilla/";

    async function initMap() {
      // Crear el mapa y centrarlo en una ubicación predeterminada
      map = new google.maps.Map(document.getElementById("map"), {
        center: { lat: -34.657713050818785, lng: -58.63239669756467 },
        zoom: 13
      });
  
      cargarServicios();
      gpsMovil()

      // Crea un marcador (será movido después según la dirección)
      marker = new google.maps.Marker({
        map: map,
      });

      // Crear el servicio de autocompletado
      var input = document.getElementById("address");
      var autocomplete = new google.maps.places.Autocomplete(input);
  
      // Asocia el autocompletado con el mapa
      autocomplete.bindTo("bounds", map);
  
      // Define lo que sucede cuando se selecciona una opción del autocompletado
      autocomplete.addListener("place_changed", function () {
        var place = autocomplete.getPlace();
  
        // Verifica que el lugar sea válido
        if (!place.geometry) {
          return;
        }
  
        // Mueve el mapa a la ubicación seleccionada
        map.setCenter(place.geometry.location);
        map.setZoom(15);
  
        // Mueve el marcador a la nueva ubicación
        marker.setPosition(place.geometry.location);
        marker.setVisible(true);
      });

          // Crear una nueva capa de datos para el polígono
        var zonasLayer = new google.maps.Data();

        zonasLayer.loadGeoJson(ZONAS_JSON_URL);

        // Diccionario de colores por nombre de zona
        const zonaColors = {
            "Destacamento N°2": "#FF0000",
            "Cuartel Central": "#e0d600",
            "Destacamento N°1": "#0000FF",
        };

        // Aplicar estilo dinámicamente
        zonasLayer.setStyle(function(feature) {
            var nombreZona = feature.getProperty("Name"); // Asegúrate de que el GeoJSON tenga la propiedad "nombre"
            var color = zonaColors[nombreZona] || "#000000"; // Si no encuentra el nombre, usa negro por defecto

            return {
                fillColor: color,
                fillOpacity: 0.4,
                strokeColor: color,
                strokeOpacity: 0.8,
                strokeWeight: 2
            };
        });

        // Agregar la capa al mapa
        zonasLayer.setMap(map);

    // Crear la capa para hidrantes
    hidrantesLayer = new google.maps.Data();
    cuartelesLayer = new google.maps.Data();
    infoWindow = new google.maps.InfoWindow();

        // Cargar el archivo GeoJSON de hidrantes en la capa
        hidrantesLayer.loadGeoJson(HIDRANTES_JSON_URL, null, function(features) {
            features.forEach(function (feature) {
                var coords = feature.getGeometry().get();
                var latLng = new google.maps.LatLng(coords.lat(), coords.lng());

                // Obtener el nombre y la descripción del GeoJSON
                var name = feature.getProperty("name") || "Hidrante";
                var description = feature.getProperty("description") || "Sin descripción";
                var icon = feature.getProperty("icon") || "Sin descripción";

                let icono = {
                    url: HIDRANTES_PNG_URL, // url
                    scaledSize: new google.maps.Size(40, 40), // scaled size
                    origin: new google.maps.Point(0,0), // origin
                    anchor: new google.maps.Point(20, 40) // anchor
                };

                // Crear un marcador por cada hidrante
                var hidranteMarker = new google.maps.Marker({
                    position: latLng,
                    map: null,
                    icon: icono,
                    title: name, // Nombre del hidrante
                });

                // Evento para mostrar la información en un popup al hacer clic
                google.maps.event.addListener(hidranteMarker, 'click', function () {
                    infoWindow.setContent(`<strong>${name}</strong><br>${description}`);
                    infoWindow.open(map, hidranteMarker);
                });

                // Almacenar el marcador en el array
                hidrantesMarkers.push(hidranteMarker);
            });
        });

        hidrantesLayer.setMap(null); // 🔴 Ocultar hidrantes al inicio

        // Cargar el archivo GeoJSON de hidrantes en la capa
        cuartelesLayer.loadGeoJson(CUARTELES_JSON_URL, null, function(features) {
            features.forEach(function (feature) {
                var coords = feature.getGeometry().get();
                var latLng = new google.maps.LatLng(coords.lat(), coords.lng());

                // Obtener el nombre y la descripción del GeoJSON
                var name = feature.getProperty("name") || "Hidrante";
                var description = feature.getProperty("description") || "Sin descripción";
                var icon = feature.getProperty("icon") || "Sin descripción";

                let icono  = {
                    url: PNG_URL+icon, // url
                    scaledSize: new google.maps.Size(40, 40), // scaled size
                    origin: new google.maps.Point(0,0), // origin
                    anchor: new google.maps.Point(20, 40) // anchor
                };
                // Crear un marcador por cada hidrante
                var cuartelMarker = new google.maps.Marker({
                    position: latLng,
                    map: map,
                    icon: icono,
                    title: name, // Nombre del cuartel
                });

                // Evento para mostrar la información en un popup al hacer clic
                google.maps.event.addListener(cuartelMarker, 'click', function () {
                    infoWindow.setContent(`<strong>${name}</strong><br>${description}`);
                    infoWindow.open(map, cuartelMarker);
                });

                // Almacenar el marcador en el array
                cuartelesMarkers.push(cuartelMarker);
            });
        });
        console.log("Nuevo estado de hidrantesLayer:", hidrantesLayer.getMap());


}

let movilMarker = null;  // Variable global para el marcador del móvil

function gpsMovil() {

    
    socket.onmessage = function(e) {
        var data = JSON.parse(e.data);
        var lat = data.latitude;
        var lng = data.longitude;

        if (!movilMarker) {
            movilMarker = new google.maps.Marker({
                position: { lat: lat, lng: lng },
                map: map,
                title: "Móvil",
                icon: {
                    url: "/static/images/movil.png",
                    scaledSize: new google.maps.Size(40, 40)
                }
            });
        } else {
            movilMarker.setPosition({ lat: lat, lng: lng });
        }
    };
}




socketServicios.onmessage = function(event) {
    try {
        var data = JSON.parse(event.data);
        console.log("Mensaje WebSocket recibido:", data);

        // Si el mensaje indica que un servicio ha finalizado
        if (data.tipo === "finalizar_servicio" && data.servicio) {
            console.log("Eliminando marcador para servicio ID:", data.servicio.id);
            eliminarMarcador(data.servicio.id);
            return;
        }

        // Si es un nuevo servicio, agregarlo al mapa
        if (data.tipo === "nuevo_servicio" && data.servicio) {
            console.log("Agregando nuevo servicio ID:", data.servicio.id);
            agregarMarcador(data.servicio);
            return;
        }
        
    } catch (error) {
        console.error("Error procesando los datos del WebSocket:", error);
    }
};


function agregarMarcador(servicio) {
    var lat = parseFloat(servicio.latitud);
    var lng = parseFloat(servicio.longitud);

    // Si en el mensaje WebSocket el tipo viene como objeto (con id y tipo),
    // se usa directamente. En caso contrario, se busca en una variable global.
    let serviciotipo;
    if (typeof servicio.tipo === "object" && servicio.tipo !== null) {
        serviciotipo = servicio.tipo;
    } else {
        // Si 'tiposervicio' es una variable global con los tipos, se busca allí.
        serviciotipo = window.tiposervicio ? window.tiposervicio.find(t => t.id == servicio.tipo) : { tipo: "default" };
    }

    // Definir el icono personalizado
    let icono = {
        url: PNG_URL + 'images/' + (serviciotipo ? serviciotipo.tipo : "default") + ".png",
        scaledSize: new google.maps.Size(40, 40),
        origin: new google.maps.Point(0, 0),
        anchor: new google.maps.Point(20, 20)
    };

    // Crear el marcador con el pin personalizado
    let marker = new google.maps.Marker({
        position: { lat: lat, lng: lng },
        map: map,
        icon: icono,
        title: serviciotipo ? serviciotipo.tipo : "Servicio"
    });

    // Crear una ventana de información (opcional)
    let infowindow = new google.maps.InfoWindow({
        content: `<strong>${serviciotipo ? serviciotipo.tipo : "Servicio"}</strong>`
    });

    marker.addListener("click", function () {
        infowindow.open(map, marker);
    });

    // Asignar el ID del servicio al marcador (convirtiéndolo a string para coincidencias)
    marker.id = servicio.id.toString();

    // Guardar el marcador en el array y también en el objeto markers para búsqueda rápida
    markers.push(marker);
    markers[servicio.id] = marker;

    console.log("✅ Marcador agregado para servicio ID:", servicio.id);
}

function actualizarMarcador(servicio) {
    let idServicio = servicio.id.toString();
    let marker = markers[idServicio];
    if (marker) {
        // Actualizar la posición si se ha modificado
        if (servicio.latitud && servicio.longitud) {
            let nuevaPos = new google.maps.LatLng(
                parseFloat(servicio.latitud),
                parseFloat(servicio.longitud)
            );
            marker.setPosition(nuevaPos);
        }
        // Actualizar el título y forzar la actualización del icono
        if (servicio.tipo && servicio.tipo.tipo) {
            // Construir la URL del icono con un parámetro temporal para forzar recarga
            let newIconUrl = PNG_URL + "images/" + servicio.tipo.tipo + ".png" + "?t=" + new Date().getTime();
            let newIcon = {
                url: newIconUrl,
                scaledSize: new google.maps.Size(40, 40),
                origin: new google.maps.Point(0, 0),
                anchor: new google.maps.Point(20, 20)
            };
            // Forzar que el marker borre el icono y luego se actualice
            marker.setIcon(null);
            marker.setIcon(newIcon);
            marker.setTitle(servicio.tipo.tipo);
        }
        console.log("Marcador actualizado para servicio ID:", servicio.id);
    } else {
        console.warn("No se encontró marcador para servicio ID:", servicio.id);
    }
}

function eliminarMarcador(servicioId) {
    servicioId = servicioId.toString();  // Convertir a string para asegurar coincidencia
    console.log("Intentando eliminar marcador del servicio ID:", servicioId);

    // Buscar el marcador en el array markers
    for (var i = 0; i < markers.length; i++) {
        if (markers[i].id === servicioId) {
            markers[i].setMap(null);  // Quita el marcador del mapa
            markers.splice(i, 1);  // Eliminar del array markers
            console.log("✅ Marcador eliminado con éxito (array):", servicioId);
            return;
        }
    }

    // Buscar el marcador en el objeto markers
    if (markers[servicioId]) {
        markers[servicioId].setMap(null);
        delete markers[servicioId];
        console.log("✅ Marcador eliminado del objeto markers:", servicioId);
        return;
    }

    console.warn("⚠️ No se encontró el marcador con ID:", servicioId);
}

function cargarServicios() {
    fetch("/obtener_servicios/")
        .then(response => {
            if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
            return response.json();
        })
        .then(data => {
            let servicios = data.servicios;
            let tiposervicio = data.tiposervicio;
            let serviciosNuevos = new Set();

            // Inicializar OverlappingMarkerSpiderfier
            let oms = new OverlappingMarkerSpiderfier(map, {
                markersWontMove: true,
                markersWontHide: true,
                basicFormatEvents: true
            });

            servicios.forEach(servicio => {
                // Verificar que el servicio tenga un id
                if (!servicio.id) {
                    console.warn("Servicio sin id, omitiendo:", servicio);
                    return;
                }

                let latitud = parseFloat(servicio.latitud);
                let longitud = parseFloat(servicio.longitud);
                if (isNaN(latitud) || isNaN(longitud)) {
                    console.error("⚠️ Servicio con datos inválidos:", servicio);
                    return;
                }

                // Usar el id del servicio como clave (como string)
                let idServicio = servicio.id.toString();
                serviciosNuevos.add(idServicio);

                if (!markers[idServicio]) {
                    let serviciotipo = tiposervicio.find(t => t.id === servicio.tipo);
                    let icono = {
                        url: PNG_URL + "images/" + (serviciotipo ? serviciotipo.tipo : "default") + ".png",
                        scaledSize: new google.maps.Size(40, 40),
                        origin: new google.maps.Point(0, 0),
                        anchor: new google.maps.Point(20, 20)
                    };

                    let marker = new google.maps.Marker({
                        position: { lat: latitud, lng: longitud },
                        map: map,
                        icon: icono,
                        title: serviciotipo ? serviciotipo.tipo : "Servicio"
                    });

                    let infowindow = new google.maps.InfoWindow({
                        content: `<strong>${serviciotipo ? serviciotipo.tipo : "Servicio"}</strong>`
                    });

                    marker.addListener("click", function () {
                        infowindow.open(map, marker);
                    });

                    oms.addMarker(marker);

                    markers[idServicio] = marker;
                    console.log("Marcador agregado para servicio ID:", idServicio);
                }
            });

            // Eliminar marcadores que ya no existen en los nuevos datos
            Object.keys(markers).forEach(id => {
                if (!serviciosNuevos.has(id)) {
                    markers[id].setMap(null);
                    delete markers[id];
                }
            });
        })
        .catch(error => console.error("Error al obtener los servicios:", error));
}


// Alternar la visibilidad de los marcadores de hidrantes
document.getElementById("hidrantes").addEventListener("click", function() {
    if (hidrantesMarkers.length > 0 && hidrantesMarkers[0].getMap()) {
        console.log("Ocultando hidrantes");
        hidrantesMarkers.forEach(marker => marker.setMap(null));
    } else {
        console.log("Mostrando hidrantes");
        hidrantesMarkers.forEach(marker => marker.setMap(map));
    }
});

// Alternar la visibilidad de los marcadores de cuarteles
document.getElementById("cuarteles").addEventListener("click", function() {
// Alternar entre mostrar y ocultar los marcadores
cuartelesMarkers.forEach(function(marker) {
  if (marker.getMap()) {
    marker.setMap(null);  // Ocultar el marcador
  } else {
    marker.setMap(map);  // Mostrar el marcador
  }
});
});

// Cargar el mapa cuando la página esté lista
// google.maps.event.addDomListener(window, "load", initMap);
window.addEventListener("load", initMap)
