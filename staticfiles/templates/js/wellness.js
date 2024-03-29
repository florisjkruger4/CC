let show_fullname, show_pos, show_trends;
let today;

let wellness_AJAXurl;

document.addEventListener("DOMContentLoaded", function () {
  // Get today's date as a string in the format "yyyy-mm-dd"
  today = new Date().toISOString().substring(0, 10);

  wellness_AJAXurl = window.wellnessData.url;

  // Set the value of the date input to today's date
  document.getElementById("wellnessdate").value = today;
  document.getElementById("wellnessdate").ariaValueMax = today;

  // control variables for display settings
  show_fullname = true;
  show_pos = true;
  show_trends = true;

  // checks for a date or team change
  document.getElementById("wellnessdate").addEventListener("change", check_both_inputs);
  document.getElementById("wellnesssport").addEventListener("change", check_both_inputs);

  // checks for settings updates
  document.getElementById("i-show_fullname").addEventListener("change", update_name_display);
  document.getElementById("i-show_trends").addEventListener("change", update_trends_display);
  document.getElementById("i-show_pos").addEventListener("change", update_pos_display);
});

// update athlete names by setting "show_fullname" to true or false depending on
// user checkbox selection. upon change of a checkbox, submit another
// ajax request to update the page
function update_name_display() {

  let all_names_full = document.getElementsByClassName('ath-full-name');
  let all_names = document.getElementsByClassName('ath-name');

  if (document.getElementById("i-show_fullname").checked) {
    for (let i = 0; i < all_names_full.length; i++)
      all_names_full[i].style.display = "block";
    for (let i = 0; i < all_names.length; i++)
      all_names[i].style.display = "none";
  }
  else {
    for (let i = 0; i < all_names_full.length; i++)
      all_names_full[i].style.display = "none";
    for (let i = 0; i < all_names.length; i++)
      all_names[i].style.display = "block";

  }
}

// update trend graphs by setting "show_trends" to true or false depending on
// user checkbox selection. upon change of a checkbox, submit another
// ajax request to update the page
function update_trends_display() {
  if (document.getElementById("i-show_trends").checked)
    show_trends = true;
  else
    show_trends = false;

  console.log(show_trends);

  check_both_inputs();
}

// update position by setting "show_pos" to true or false depending on
// user checkbox selection. upon change of a checkbox, submit another
// ajax request to update the page
function update_pos_display() {

  let all_pos = document.getElementsByClassName('ath-pos');

  if (document.getElementById("i-show_pos").checked) {
    for (let i = 0; i < all_pos.length; i++)
      all_pos[i].style.display = "block";
  }
  else {
    for (let i = 0; i < all_pos.length; i++)
      all_pos[i].style.display = "none";
  }
}

//checks that both a team and a date are selected before submitting an ajax request
function check_both_inputs() {
  if (document.getElementById("wellnessdate").value && document.getElementById("wellnesssport").value)
    wellness_ajax();
}

/* When the "#wellnessform" form is submitted, this function will send an AJAX request to fetch the new data. */
function wellness_ajax() {
  // Get value of #sportsteam
  var date_selected = document.getElementById("wellnessdate").value
  var sport_selected = document.getElementById("wellnesssport").value

  //add loading circle
  $("#header").append("<div id=\"loading\" class=\"lds-dual-ring-small\"></div>");

  disable_inputs();

  // Send "POST" AJAX request to url 'AthleteProf'
  // This request will be handled by the Django backend -> see views.py recordKPI() for that code
  $.ajax({
    //URL needs to be fname, lname, DOB for athletes
    url: wellness_AJAXurl,
    type: "POST",
    dataType: "json",
    data: JSON.stringify({ wellnessdate: date_selected, sportsteam: sport_selected, show_trends: show_trends }),
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCookie("csrftoken"),  // don't forget to include the 'getCookie' function
    },
    success: (response) => {

      console.log(response);

      // hide how-to message and remove loading animation
      $("#how-to").hide();
      $("#loading").remove();

      //$("#header-text").innerText = "Wellness - " + sport_selected;

      // get "template" for card to be cloned for each athlete's wellness card
      const template = document.getElementById("base");

      //clear form
      document.getElementById("forms").innerHTML = "";

      // loop thru all athletes on specified team
      for (var key in response.athletes) {

        //declare athlete info
        var name = "", fullname = "", pos = "", picURL = "";

        //declare athlete wellness info
        var hoursofsleep = 0, sleepquality = 0, breakfast = 0,
          hydration = 0, soreness = 0, stress = 0, mood = 0;
        var status = "None", total = 0, trend = "", date = "";

        // get athlete name, position, and photo
        // only show last name unless "show_fullname" is true
        name = response.athletes[key].lname;
        fullname = response.athletes[key].fname + " " + response.athletes[key].lname;

        template.getElementsByClassName('ath-name')[0].innerText = name;
        template.getElementsByClassName('ath-full-name')[0].innerText = fullname;

        console.log(template.getElementsByClassName('ath-name'));
        console.log(template.getElementsByClassName('ath-full-name'));

        pos = response.athletes[key].position;
        template.getElementsByClassName('ath-pos')[0].innerText = pos;

        // get directory to athlete image
        picURL = response.athletes_img[key];

        // get individual values needed for wellness total and then sum them
        hoursofsleep = Number(response.wellness[key].hoursofsleep);
        sleepquality = Number(response.wellness[key].sleepquality);
        breakfast = Number(response.wellness[key].breakfast);
        hydration = Number(response.wellness[key].hydration);
        soreness = Number(response.wellness[key].soreness);
        stress = Number(response.wellness[key].stress);
        mood = Number(response.wellness[key].mood);

        total = hoursofsleep + sleepquality + breakfast +
          hydration + soreness + stress + mood;

        // get status
        status = response.wellness[key].status;

        // show position if one exists, and if the option is checked


        template.querySelector("#ath-img").setAttribute("src", picURL);

        // inject wellness stats into template
        template.querySelector("#Hoursofsleep").innerText = hoursofsleep;
        template.querySelector("#Sleepquality").innerText = sleepquality;
        template.querySelector("#Breakfast").innerText = breakfast;
        template.querySelector("#Hydration").innerText = hydration;
        template.querySelector("#Soreness").innerText = soreness;
        template.querySelector("#Stress").innerText = stress;
        template.querySelector("#Mood").innerText = mood;

        // inject the date of this wellness date into te plate
        date = response.wellness[key].date;
        if (date)
          template.querySelector("#date-recorded").innerText = date;
        else
          template.querySelector("#date-recorded").innerText = "No Date";


        // change color of "status" depending on if an athlete is "good" (in) or "out" (out, obviously...)
        if (status == "Out") {
          template.querySelector("#status").style.color = "black";
          template.querySelector("#status").innerText = "Out";
          template.querySelector("#status-box").style.backgroundColor = "var(--acc-color-neg)";
        }
        else if (status == "Good") {
          template.querySelector("#status").style.color = "black";
          template.querySelector("#status").innerText = "Good";
          template.querySelector("#status-box").style.backgroundColor = "var(--acc-color-pos)";
        }
        //if there is no status, set it to gray
        else {
          template.querySelector("#status").innerText = "None";
          template.querySelector("#status-box").style.backgroundColor = "var(--color-primary)";
        }

        template.querySelector("#readiness").innerText = "Readiness: " + total;

        // by default, do not show trend block
        template.getElementsByClassName('trend-display')[0].style.display = "none";

        // if the user would like to display trends...
        if (show_trends) {
          // make trends section visible (hidden if show_trends is false)
          template.getElementsByClassName('trend-display')[0].style.display = "block";

          // reset innerhtml and innertext of trend graph to avoid past
          // data interferring with new requests
          template.getElementsByClassName('trend-graph')[0].innerHTML = "";
          template.getElementsByClassName('trend-graph')[0].innerText = "";

          // get trend graph (will be null if there isn't one)
          trend = response.wellness_trends[key];

          if (trend)
            template.getElementsByClassName('trend-graph')[0].innerHTML += "<img src=\"data:image/png;base64, " + trend + "\">";
          else
            template.getElementsByClassName('trend-graph')[0].innerText = "No Trend Data";
        }

        // clone the template and add it to the list of forms
        document.getElementById("forms").append(template.cloneNode(true));

        enable_inputs();

        update_name_display();
        update_pos_display();
      }
    },
    error: (error) => {

      console.log(error);
      alert("Error processing Ajax Request");

      enable_inputs();
    }
  })
}
