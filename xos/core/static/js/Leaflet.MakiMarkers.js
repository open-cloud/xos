
/*
 * Copyright 2017-present Open Networking Foundation

 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at

 * http://www.apache.org/licenses/LICENSE-2.0

 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */


/*
 * Leaflet plugin to create map icons using Maki Icons from MapBox.
 *
 * References:
 *   Maki Icons: https://www.mapbox.com/maki/
 *   MapBox Marker API: https://www.mapbox.com/developers/api/#Stand-alone.markers
 *
 * Usage:
 *   var icon = L.MakiMarkers.icon({icon: "rocket", color: "#b0b", size: "m"});
 *
 * License:
 *   MIT: http://jseppi.mit-license.org/
 */
(function () {
  "use strict";
  L.MakiMarkers = {
    // Available Maki Icons
    icons: ["circle-stroked", "circle", "square-stroked", "square",
      "triangle-stroked", "triangle", "star-stroked", "star", "cross",
      "marker-stroked", "marker", "religious-jewish", "religious-christian",
      "religious-muslim", "cemetery", "rocket", "airport", "heliport", "rail",
      "rail-metro", "rail-light", "bus", "fuel", "parking", "parking-garage",
      "airfield", "roadblock", "ferry", "harbor", "bicycle", "park", "park2",
      "museum", "lodging", "monument", "zoo", "garden", "campsite", "theatre",
      "art-gallery", "pitch", "soccer", "america-football", "tennis", "basketball",
      "baseball", "golf", "swimming", "cricket", "skiing", "school", "college",
      "library", "post", "fire-station", "town-hall", "police", "prison",
      "embassy", "beer", "restaurant", "cafe", "shop", "fast-food", "bar", "bank",
      "grocery", "cinema", "pharmacy", "hospital", "danger", "industrial",
      "warehouse", "commercial", "building", "place-of-worship", "alcohol-shop",
      "logging", "oil-well", "slaughterhouse", "dam", "water", "wetland",
      "disability", "telephone", "emergency-telephone", "toilets", "waste-basket",
      "music", "land-use", "city", "town", "village", "farm", "bakery", "dog-park",
      "lighthouse", "clothing-store", "polling-place", "playground", "entrance",
      "heart", "london-underground", "minefield", "rail-underground", "rail-above",
      "camera", "laundry", "car", "suitcase", "hairdresser", "chemist"],
    defaultColor: "#0a0",
    defaultIcon: "circle-stroked",
    defaultSize: "m",
    apiUrl: "https://api.tiles.mapbox.com/v3/marker/",
    smallOptions: {
      iconSize: [20, 50],
      popupAnchor: [0,-20]
    },
    mediumOptions: {
      iconSize: [30,70],
      popupAnchor: [0,-30]
    },
    largeOptions: {
      iconSize: [36,90],
      popupAnchor: [0,-40]
    }
  };

  L.MakiMarkers.Icon = L.Icon.extend({
    options: {
      //Maki icon: any from https://www.mapbox.com/maki/ (ref: L.MakiMarkers.icons)
      icon: L.MakiMarkers.defaultIcon,
      //Marker color: short or long form hex color code
      color: L.MakiMarkers.defaultColor,
      //Marker size: "s" (small), "m" (medium), or "l" (large)
      size: L.MakiMarkers.defaultSize,
      shadowAnchor: null,
      shadowSize: null,
      shadowUrl: null,
      className: 'maki-marker'
    },

    initialize: function(options) {
      var pin;

      options = L.setOptions(this, options);

      switch (options.size) {
        case "s":
          L.extend(options, L.MakiMarkers.smallOptions);
          break;
        case "l":
          L.extend(options, L.MakiMarkers.largeOptions);
          break;
        default:
          options.size = "m";
          L.extend(options, L.MakiMarkers.mediumOptions);
          break;
      }

      if (options.color.charAt(0) === '#') {
        options.color = options.color.substr(1);
      }

      pin = "pin-" + options.size + "-" + options.icon + "+" +
        options.color + ".png";

      options.iconUrl = "" + L.MakiMarkers.apiUrl + pin;
    }
  });

  L.MakiMarkers.icon = function(options) {
    return new L.MakiMarkers.Icon(options);
  };
})();
