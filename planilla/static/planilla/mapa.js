

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

      setInterval(cargarServicios, 5000); // Recargar cada 5 segundos

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
            "Cuartel Central": "#00FF00",
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
                    anchor: new google.maps.Point(0, 22) // anchor
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
                    anchor: new google.maps.Point(0, 40) // anchor
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

function gpsMovil(){
    var socket = new WebSocket('wss://' + window.location.host + '/ws/location/');
    socket.onmessage = function(e) {
    var data = JSON.parse(e.data);
    var lat = data.latitude;
    var lng = data.longitude;
    var speed = data.speed
    
    console.log("data: ", data)

    let marker = new google.maps.Marker({
        position: { lat: lat, lng: lng },
        map: map,
        title: "Móvil"
    });

    marker.addListener("click", function () {
        infowindow.open(map, marker);
    });
};

}

function cargarServicios() {
    fetch("/obtener_servicios/")
        .then(response => {
            if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
            return response.json();
        })
        .then(data => {
            let servicios = data.servicios;
            let tiposervicio = data.tiposervicio
            let serviciosNuevos = new Set();

            // Inicializar OverlappingMarkerSpiderfier
            let oms = new OverlappingMarkerSpiderfier(map, {
                markersWontMove: true,  // Evita que los marcadores se muevan
                markersWontHide: true,  // Evita que los marcadores desaparezcan
                basicFormatEvents: true
            });

            servicios.forEach(servicio => {
                let latitud = parseFloat(servicio.latitud);  // 🔍 Asegurar que sea número
                let longitud = parseFloat(servicio.longitud);

                if (isNaN(latitud) || isNaN(longitud)) {
                    console.error(`⚠️ Servicio con datos inválidos: `, servicio);
                    return; // 🔴 Si lat/lng no son números, no crea el marcador
                }

                let idServicio = `${servicio.direccion}-${latitud}-${longitud}`;
                serviciosNuevos.add(idServicio);

                if (!markers[idServicio]) {
                    let serviciotipo = tiposervicio.find(t => t.id === servicio.tipo);
                    let icono = {
                        url: PNG_URL + 'images/' + (serviciotipo ? serviciotipo.tipo : "default") + ".png",
                        scaledSize: new google.maps.Size(40, 40),
                        origin: new google.maps.Point(0, 0),
                        anchor: new google.maps.Point(20, 20)
                    }

                    let marker = new google.maps.Marker({
                        position: { lat: latitud, lng: longitud },
                        map: map,
                        icon: icono,
                        title: serviciotipo.tipo
                    });

                    let infowindow = new google.maps.InfoWindow({
                        content: `<strong>${serviciotipo.tipo}</strong>`
                    });

                    marker.addListener("click", function () {
                        infowindow.open(map, marker);
                    });

                    // Agregar el marcador al spiderfier
                    oms.addMarker(marker);

                    markers[idServicio] = marker;

                    console.log(markers)
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
