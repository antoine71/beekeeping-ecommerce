// select fiedl toggler

const mondialRelayRadio = document.getElementById("id_delivery_option_1");
const zoneWidget = document.getElementById("Zone_Widget");
const deliveryOptionRadios = document.querySelectorAll(
  "input[name=delivery_option]"
);

for (radio of deliveryOptionRadios) {
  radio.addEventListener("change", toggleMondialRelayWidget);
}

document.addEventListener("DOMContentLoaded", toggleMondialRelayWidget);

function toggleMondialRelayWidget() {
  if (mondialRelayRadio.checked) {
    zoneWidget.style.display = "block";
  } else {
    zoneWidget.style.display = "none";
  }
}

// add hidden inputs for each mondial relay field

function appendHiddenInputs(data) {
  const formElt = document.getElementById("checkout_form");
  for (const [category, value] of Object.entries(data)) {
    const input = createInput(category, value);
    formElt.append(input);
  }
}

// create inputs for mondial relay fields

function createInput(category, value) {
  input = document.getElementById(`mr_${category}`);
  if (!input) {
    input = document.createElement("input");
  }
  input.setAttribute("type", "hidden");
  input.setAttribute("id", `mr_${category}`);
  input.setAttribute("name", `mr_${category}`);
  input.setAttribute("value", value);
  return input;
}

// Init the widget on ready state

$(document).ready(function () {
  // Loading the Parcelshop picker widget into the <div> with id "Zone_Widget" with such settings:
  $("#Zone_Widget").MR_ParcelShopPicker({
    //
    // Settings relating to the HTML.
    //
    // JQuery selector of the HTML element receiving the Parcelshop Number (ex: here, input type text, but should be input hidden)
    Target: "#Target_Widget",
    //
    // Settings for Parcelshop data access
    //
    // Code given by Mondial Relay, 8 characters (padding right with spaces)
    // BDTEST is used for development only => a warning appears
    Brand: "BDTEST  ",
    // Default Country (2 letters) used for search at loading
    Country: "FR",
    AllowedCountries: ["FR"],
    // Delivery mode (Standard [24R], XL [24L], XXL [24X], Drive [DRI])
    ColLivMod: "24R",
    // Number of parcelshops requested (must be less than 20)
    NbResults: "7",
    //
    // Display settings
    //
    // Enable Responsive (nb: non responsive corresponds to the Widget used in older versions=
    Responsive: true,
    // Show the results on Leaflet map usng OpenStreetMap.
    ShowResultsOnMap: false,

    OnParcelShopSelected: function (data) {
      appendHiddenInputs(data);
    },
  });
});
