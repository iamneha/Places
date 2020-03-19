/**
 * Moves the map to display over Berlin
 *
 * @param  {H.Map} map      A HERE Map instance within the application
 */

var platform = new H.service.Platform({
  apikey: window.API_KEY
});
var defaultLayers = platform.createDefaultLayers();

function moveMapToGivenCoordinates(map) {
  var cordinates = getCoordinates()

  if (cordinates.lat && cordinates.lng) {
    map.setCenter({
      lat: cordinates.lat,
      lng: cordinates.lng
    });
    map.setZoom(14);
  } else {
    map.setCenter({
      lat: 52.5159,
      lng: 13.3777
    });
  }
}

function getCoordinates() {
  var Latitude = document.getElementById("latitude");
  var Longitude = document.getElementById("longitude");

  if (Latitude && Longitude) {
    return {
      lat: Latitude['value'],
      lng: Longitude['value']
    }
  }
}

function addMarkerToGroup(group, coordinate, html) {
  var marker = new H.map.Marker(coordinate);
  marker.setData(html);
  group.addObject(marker);
}

function hotelBookings(username, email, latitude, longitude, property_name) {
  var booking_params = {}

  booking_params['username'] = username
  booking_params['email'] = email
  booking_params["property_name"] = property_name
  booking_params["property_latitude"] = longitude
  booking_params["property_longitude"] = latitude

  $.ajax({
    type: 'POST',
    url: window.BOOKING_URL,
    data: JSON.stringify(booking_params),
    contentType: 'application/json',
    statusCode: {
      200: function () {
        alert("Successfully booked!");
      }
    }
  })
}


function addInfoBubble(map, hotelsFromCoordinates = null) {
  var group = new H.map.Group();

  map.addObject(group);
  group.addEventListener('tap', function (evt) {
    var bubble = new H.ui.InfoBubble(evt.target.getGeometry(), {
      content: evt.target.getData()
    });
    ui.addBubble(bubble);
  }, false);


  if (hotelsFromCoordinates != null) {
    var hotelsFromCoordinatesLength = hotelsFromCoordinates.length

    for (var i = 0; i < hotelsFromCoordinatesLength; i++) {
      var curr_lat = hotelsFromCoordinates[i]['position'][0]
      var curr_lng = hotelsFromCoordinates[i]['position'][1]
      var curr_title = hotelsFromCoordinates[i]['title']
      addMarkerToGroup(
        group, {
          lat: curr_lat,
          lng: curr_lng
        },
        '<div>' + curr_title +
        '<form>' +
        '<input type="text" id="bookWithUsername" name="username" placeholder="username"><br>' +
        '<input type="email" id="bookwithEmail" name="email" placeholder="email"><br><br>' +
        '<button type="button"' +
        'onclick="hotelBookings(' + "document.getElementById('bookWithUsername').value" + ',' +
        "document.getElementById('bookwithEmail').value" + ',' + curr_lat + ',' + curr_lng + ',\'' + curr_title + '\')" > Book</button > ' +
        '</form></div>'
      );
    }
  }
}

function getLocationFromCoordinates() {
  var Latitude = document.getElementById("latitude");
  var Longitude = document.getElementById("longitude");
  var params = {
    at: Latitude['value'] + ',' + Longitude['value']
  }

  $.get(window.PROPERTY_URL, params,
    function (data, status) {
      if (status === 'success') {
        moveMapToGivenCoordinates(infomap)
        addInfoBubble(infomap, data)
      }
    }
  );
}

var infomap = new H.Map(document.getElementById('map'),
  defaultLayers.vector.normal.map, {
    center: {
      lat: 50,
      lng: 5
    },
    zoom: 4,
    pixelRatio: window.devicePixelRatio || 1
  }
);
window.addEventListener('resize', () => infomap.getViewPort().resize());
var behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(infomap));
var ui = H.ui.UI.createDefault(infomap, defaultLayers);

window.onload = function () {
  addInfoBubble(infomap)
  moveMapToGivenCoordinates(infomap)
}