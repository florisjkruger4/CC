/* getCookie() function definition*/
// Definition for "getCookie" function, which will return a cookie from the document matching the parameter "name".
// This is a utility funciton utilized to send and AJAX request (see next code block)

// Cookie is initialized to null
// If there is are document cookies and they are NOT empty, the cookies in the document are fetched and placed in an array
// This array is searched for a cookie that matches parameter "name"
// If such a cookie is found, it is returned.
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//jQuery for functionality of "tabs"
$(document).ready(function () {
    // upon click of cog wheel "settings", show the options card
    // if it's already showing, close it. functions as a toggle
    $("#settings").click(function () {
        if ($('#options-card').is(':hidden')) {
            $("#options-card").show();
        } else {
            $("#options-card").hide();
        }
    });

    // if the user clicks anywhere but the options card, close the settings menu
    let options_card = document.getElementById("settings");
    document.addEventListener('click', (event) => {
        if (!options_card.contains(event.target)) {
            $("#options-card").hide();
        }
    });

    $(".clickable-row").click(function() {
        window.location = $(this).data("href");
    });
});

// used to prevent additional user input while an ajax request is processing
// prevents garbled data

function disable_inputs() {
    
    //disable all checkboxes, radios, dates, and selectors
    document.querySelectorAll("input[type=checkbox]").forEach(checkbox => {
        checkbox.disabled = true;
    })
    document.querySelectorAll("input[type=radio]").forEach(radio => {
        radio.disabled = true;
    })
    document.querySelectorAll("input[type=date]").forEach(date => {
        date.disabled = true;
    })
    document.querySelectorAll("input[type=select]").forEach(select => {
        select.disabled = true;
    })
}
function enable_inputs() {

    // enable all checkboxes, radios, dates, and selectors
    document.querySelectorAll("input[type=checkbox]").forEach(checkbox => {
        checkbox.disabled = false;
    })
    document.querySelectorAll("input[type=radio]").forEach(radio => {
        radio.disabled = false;
    })
    document.querySelectorAll("input[type=date]").forEach(date => {
        date.disabled = false;
    })
    document.querySelectorAll("input[type=select]").forEach(select => {
        select.disabled = false;
    })
}