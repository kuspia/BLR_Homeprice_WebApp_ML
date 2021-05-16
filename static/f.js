function getBathValue() {
  var uiBathrooms = document.getElementsByName("uiBathrooms");
  for (var i in uiBathrooms) {
    if (uiBathrooms[i].checked) {
      return parseInt(i) + 1;
    }
  }
  return -1; // Invalid Value
}
function getBHKValue() {
  var uiBHK = document.getElementsByName("uiBHK");
  for (var i in uiBHK) {
    if (uiBHK[i].checked) {
      return parseInt(i) + 1;
    }
  }
  return -1; // Invalid Value
}
function onClickedEstimatePrice() {
  console.log("Estimate price button clicked right now");
  var sqft = document.getElementById("uiSqft");
  var bhk = getBHKValue();
  var bathrooms = getBathValue();
  var location = document.getElementById("uiLocations");
  var estPrice = document.getElementById("uiEstimatedPrice");

  var url = "https://findhomeprice.herokuapp.com/predict_home_price";

  $.post(
    url,
    {
      total_sqft: parseFloat(sqft.value),
      bhk: bhk,
      bath: bathrooms,
      location: location.value,
    },
    function (data, status) {
      console.log(data.estimated_price);

      if(data.estimated_price>0)
      {

      estPrice.innerHTML = "<h2>" + data.estimated_price.toString() + " Lakh</h2>";
      console.log(status);

      }
      else
      {

      estPrice.innerHTML = "<h2 style='color:red;' > <strong> ERROR!!   </strong></h2>";
      window.alert('Please choose the values that are dimensionally feasible for home');
      console.log(status);

      }

    }
  );
}

function onPageLoad() {
  console.log("document loaded");

  var url = "https://findhomeprice.herokuapp.com/get_location_names";

  $.get(url, function (data, status) {
    console.log("got response for get_location_names request");
    if (data) {
      var locations = data.locations;
      var uiLocations = document.getElementById("uiLocations");
      $("#uiLocations").empty();
      for (var i in locations) {
        var opt = new Option(locations[i]);
        $("#uiLocations").append(opt);
      }
    }
  });
}

window.onload = onPageLoad;
