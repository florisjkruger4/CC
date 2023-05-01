let groups_AJAXurl;
let is_loading_kpi = false;

let date1, date2;
let radioButtons;
let raw_graph_genderAVG_selection, raw_graph_teamAVG_selection, T_score_radio_buttons;

document.addEventListener("DOMContentLoaded", function () {
    groups_AJAXurl = window.groupsData.url;

    // hide bar graph div
    $("#bar-graphs").hide();

    // selects all radio button options
    radioButtons = document.querySelectorAll('.radiotest');

    // gets the date selectors
    date1 = document.getElementById("date1");
    date2 = document.getElementById("date2");

    // enables the date selectors when you select a radio button first
    for (i of radioButtons) {
        i.addEventListener('click', function (e) {
            console.log("selected");
            //document.getElementById("kpiform").style.opacity = "100%";
            date1.disabled = false;
            date2.disabled = false;
            if (date1.value && date2.value) {
                kpi_teams();
            }
        })
    }

    T_score_radio_buttons = document.querySelectorAll('.radioBTN');
    for (j of T_score_radio_buttons) {
        j.addEventListener('click', function (e) {
            kpi_teams();
        })
    }

    raw_graph_teamAVG_selection = document.getElementById("t_AVG");
    raw_graph_teamAVG_selection.onclick = function () {
        kpi_teams();
    }

    raw_graph_genderAVG_selection = document.getElementById("g_AVG");
    raw_graph_genderAVG_selection.onclick = function () {
        kpi_teams();
    }

    // checks when all 3 selection have been made (radio button, date1 and date2)
    date1.onchange = function () {
        if (date1.value && date2.value) {
            $("#settings").show();
            $("#how-to-teams").hide();
            $("#bar-graphs").show();
            kpi_teams();
        }
    }
    date2.onchange = function () {
        if (date1.value && date2.value) {
            $("#settings").show();
            $("#how-to-teams").hide();
            $("#bar-graphs").show();
            kpi_teams();
        }
    }
});

// hides/shows tests when their corresponding checkmark in the options tab is checked/unchecked
function hide_tests() {
    document.querySelectorAll("[type=checkbox]").forEach(checkbox => {
        checkbox.addEventListener("click", function (e) {

            // get id of this checkbox
            id = this.id;
            console.log(id);
            if (this.checked) {

                // concatenate respective ids of bar and trend graphs
                $("#bar_" + id).show();
                $("#z_" + id).show();
            }
            else {
                // concatenate respective ids of bar and trend graphs
                $("#bar_" + id).hide();
                $("#z_" + id).hide();
            }
            e.stopPropagation();
        })
    })
}

function kpi_teams() {

    var all_Athletes = document.getElementById("vbtn-radio1")
    var all_Males = document.getElementById("vbtn-radio2")
    var all_Females = document.getElementById("vbtn-radio3")

    var t_rad = document.getElementById("t-score-radio")
    var r_rad = document.getElementById("raw-score-radio")

    if (all_Athletes.checked == true || all_Males.checked == true || all_Females.checked == true) {
        $("#t-score-selections").hide();
        $("#raw-score-selections").hide();
    }
    else if (t_rad.checked == true) {
        $("#t-score-selections").show();
    }
    else if (r_rad.checked == true) {
        $("#raw-score-selections").show();
    }

    $("#raw-score-graphs").empty()
    $("#t-score-graphs").empty()
    $("#test-list").empty()

    $("#bar-graphs").append("<div id=\"loading-bar\" class=\"d-flex justify-content-center\"> <div class=\"lds-dual-ring\"></div></div>");

    // Get radio button values for populations or teams
    var Radio_BTN = $(".radiotest:checked").val();

    // Get radio button values for z-score graph varients
    var AVG_Radio_BTN = $(".radioBTN:checked").val();

    // gets checkbox val for gender average for raw-graphs
    var T_Avg = $("#t_AVG:checked").val();

    // gets checkbox val for gender average for raw-graphs
    var G_Avg = $("#g_AVG:checked").val();

    // AJAX function has been called! No other calls can be made until this one finishes
    is_loading_kpi = true;

    // get dates from selectors
    var date_one = document.getElementById("date1");
    var date_two = document.getElementById("date2");

    disable_inputs();

    $.ajax({
        url: groups_AJAXurl,
        type: "POST",
        dataType: "json",
        data: JSON.stringify({
            date1: date_one.value,
            date2: date_two.value,
            radiotest: Radio_BTN,
            AVG_Radio_BTN: AVG_Radio_BTN,
            t_AVG: T_Avg,
            g_AVG: G_Avg,
        }),
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        success: (response) => {
            //shows info being passed from backend
            console.log(response);

            if (response.kpi_bar.length < 1) {
                $("#raw-score-graphs").append("No Data");
            }

            if (response.z_score_bar.length < 1) {
                $("#t-score-graphs").append("No Data");
            }

            $("#loading-bar").remove()

            for (var key in response.all_testTypes) {
                let bar_template = document.getElementById("bar-template").cloneNode(true);
                let z_template = document.getElementById("z-template").cloneNode(true);

                // Construct URL for bar graph and add path to this node's img tag
                var bar_graphURL = "data:image/png;base64, " + response.kpi_bar[key];
                bar_template.querySelector("#tname").innerText = response.all_testTypes[key];
                bar_template.querySelector("#tgraph").setAttribute("src", bar_graphURL);

                // Construct URL for z-score graph and add path to this node's img tag
                var z_graphURL = "data:image/png;base64, " + response.z_score_bar[key];
                z_template.querySelector("#zname").innerText = response.all_testTypes[key];
                z_template.querySelector("#zgraph").setAttribute("src", z_graphURL);

                // Give graphs for each type an integer ID that will allow them to be maniuplated later
                bar_template.setAttribute("id", "bar_" + key);
                z_template.setAttribute("id", "z_" + key);

                $("#raw-score-graphs").append(bar_template);
                $("#t-score-graphs").append(z_template);

                var checkid = /*"check_" +*/ key;

                document.getElementById("test-list").innerHTML += "<li>" + response.all_testTypes[key] + "<input type=\"checkbox\" id=\"" + checkid + "\" checked=\"true\"></li>";

            }
            hide_tests();
            enable_inputs();

        },
        error: (error) => {
            console.log("Error processing KPI request: " + error);

        }
    })
}

$(document).ready(function () {

    $("#settings").hide();
    $("#t-score-graphs").hide();
    $("#raw-score-graphs").show();
    $("#raw-score-selections").show();
    $("#t-score-selections").hide();

    $("#t-score-radio").click(function () {
        $("#t-score-graphs").show();
        $("#raw-score-graphs").hide();
        $("#raw-score-selections").hide();

        var all_Athletes = document.getElementById("vbtn-radio1")
        var all_Males = document.getElementById("vbtn-radio2")
        var all_Females = document.getElementById("vbtn-radio3")

        if (all_Athletes.checked == true || all_Males.checked == true || all_Females.checked == true) {
            $("#t-score-selections").hide();
        }
        else {
            $("#t-score-selections").show();
        }
    });

    $("#raw-score-radio").click(function () {
        $("#raw-score-graphs").show();
        $("#t-score-graphs").hide();
        $("#t-score-selections").hide();

        var all_Athletes = document.getElementById("vbtn-radio1")
        var all_Males = document.getElementById("vbtn-radio2")
        var all_Females = document.getElementById("vbtn-radio3")

        if (all_Athletes.checked == true || all_Males.checked == true || all_Females.checked == true) {
            $("#raw-score-selections").hide();
        }
        else {
            $("#raw-score-selections").show();
        }
    });
});