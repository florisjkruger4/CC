/* Global variables for current athlete's information */
let a_fname, a_lname, a_dob, a_id, kpi_count, wellness_count;
let ajaxURL;
let tscore_loaded = false, raw_score_loaded = false;

/* Initial Page Load */
document.addEventListener("DOMContentLoaded", function () {
    a_fname = window.athleteData.fname;
    a_lname = window.athleteData.lname;
    a_dob = window.athleteData.dob;
    a_id = window.athleteData.id;
    kpi_count = window.athleteData.kpi_count;
    wellness_count = window.athleteData.wellness_count;

    ajaxURL = "/" + a_fname + "/" + a_lname + "/" + a_dob + "/" + a_id;

    // screen inits with raw score bar graphs, kpi trends, and wellness data
    // does NOT init with t-scores or spider graph
    if (kpi_count > 0) {
        raw_score_ajax();
        trends_ajax();
    }

    if (wellness_count > 0)
        wellness_ajax();

    // Create Event Listeners
    // Listens for KPI date range changes to submit new AJAX request
    document.getElementById("date1").addEventListener("change", function () {
        raw_score_loaded = false;
        tscore_loaded = false;

        raw_score_ajax();
        tscore_ajax();
        trends_ajax();
    });
    document.getElementById("date2").addEventListener("change", function () {
        raw_score_loaded = false;
        tscore_loaded = false;

        raw_score_ajax();
        tscore_ajax();
        trends_ajax();
    });

    // Listens for checked boxes for for various averages for Raw Scores
    document.getElementById("t_AVG").addEventListener("click", function () {
        raw_score_loaded = false;
        raw_score_ajax();
    });
    document.getElementById("g_AVG").addEventListener("click", function () {

        raw_score_loaded = false;
        raw_score_ajax();
    });
    document.getElementById("p_AVG").addEventListener("click", function () {
        raw_score_loaded = false;
        raw_score_ajax();
    });

    // Listens for checked radio button for T-Score averages
    document.getElementById("teamAVG").addEventListener("click", function () {
        tscore_loaded = false;
        tscore_ajax();

    });
    document.getElementById("genderAVG").addEventListener("click", function () {
        tscore_loaded = false;
        tscore_ajax();

    });
    document.getElementById("positionAVG").addEventListener("click", function () {
        tscore_loaded = false;
        tscore_ajax();

    });

    // Listens for wellness date changes 
    document.getElementById("wellnessdate").addEventListener("change", wellness_ajax);

    // if img upload changes... 
    document.getElementById("id_image").addEventListener("change", imgChange);

    // Call the spider_ajax function when the submit button is clicked
    document.getElementById("spider-submit").addEventListener("click", spider_ajax, false);
});

/* Spider Graph */
function spider_chart(athlete_results, average_results, date) {
    // Create arrays for the test names and results
    let test_names = Object.keys(athlete_results);
    let athlete_results_arr = Object.values(athlete_results);

    // Create an array of average group names
    let group_names = average_results.map(function (group_dict) {
        return group_dict.group;
    });

    // Create an array of arrays of average group results
    let group_results_arr = average_results.map(function (group_dict) {
        return Object.values(group_dict.results);
    });

    // Create the spider chart with Plotly
    let data = [{
        type: 'scatterpolar',
        r: athlete_results_arr, // Define the radius values for each data point
        theta: test_names, // Define the angle values for each data point
        fill: 'toself', // Fill the area enclosed by each data point's line
        name: 'Athlete', // Assign a label to this data series
        line: {
            color: '#96b7ff', // Set the color of the line connecting each data point
            width: 2 // Set the width of the line
        },
        // Customize the tooltip displayed when hovering over each data point
        hovertemplate: '<b>Result:</b> %{r}<br><b>Test Type:</b> %{theta}<extra></extra>'
    }];

    // Colors for team, position, and gender respectively
    let average_colors = ['green', 'yellow', 'purple'];
    let color_index = 0;
    for (let i = 0; i < group_names.length; i++) {
        // Add a trace for the group to the spider chart
        data.push({
            type: 'scatterpolar',
            r: group_results_arr[i],
            theta: test_names,
            fill: 'toself',
            name: group_names[i],
            line: {
                color: average_colors[color_index],
                width: 2
            },
            // Customize the hover over info for each data point  
            hovertemplate: '<b>Result:</b> %{r}<br><b>Test Type:</b> %{theta}<extra></extra>'
        });
        // The next trace will have a new color
        color_index += 1;
        if (color_index >= average_colors.length) {
            color_index = 0;
        }
    }

    // Update the layout of the chart
    let layout = {
        // Set the graph size, title text, font color, and size
        title: {
            text: 'Results for ' + date,
            font: {
                color: '#ffffff',
                size: 24
            },
            // Set the position of the title
            x: 0.005,
            y: 0.95
        },
        // Set the background color of the plot
        paper_bgcolor: '#1d1f26',
        // Update the styling of the radial axis
        polar: {
            // Set the background color of the circular chart
            bgcolor: '#1d1f26',
            radialaxis: {
                // Set the font color of the radial axis labels
                tickfont: {
                    color: '#ffffff'
                }
            },
            // Update the styling of the angular axis
            angularaxis: {
                // Set the font color of the angular axis labels
                tickfont: {
                    color: '#ffffff'
                }
            }
        }
    };

    $("#spider-graph").show();
    // Display the chart
    Plotly.newPlot('spider-graph', data, layout, {responsive: true} );
}

function spider_ajax(event) {
    event.preventDefault();

    disable_inputs();

    // Values to be passed to backend
    const spider_date = document.getElementById("spider_date").value;
    const test_selection = document.getElementById("selected_spider_tests");
    const avg_selection = document.getElementById("spider-avgs");

    // Select checkboxes 
    const t_checkboxes = test_selection.querySelectorAll('input[type="checkbox"]');
    const a_checkboxes = avg_selection.querySelectorAll('input[type="checkbox"]');

    // Filter the checkboxes to only include those that are checked
    const t_checked = Array.from(t_checkboxes).filter(checkbox => checkbox.checked);
    const a_checked = Array.from(a_checkboxes).filter(checkbox => checkbox.checked);

    // Get the values of the checked checkboxes
    const selected_tests = t_checked.map(checkbox => checkbox.value);
    const selected_avgs = a_checked.map(checkbox => checkbox.value);

    $.ajax({
        url: ajaxURL,
        type: "POST",
        dataType: "json",
        data: JSON.stringify({
            "req_type": "spider",
            "spider_date": spider_date,
            "selected_spider_tests": selected_tests,
            "compare_avg": selected_avgs
        }),
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        success: (response) => {
            // Call the spider chart function to display the chart
            spider_chart(response.athlete_spider_results, response.average_spider_results, response.spider_date);
            enable_inputs();
        },
        error: (error) => {

        }
    })
}

/* Raw Score & Trend Graph AJAX function */

//grabs info from the database without refreshing page and screwing everything up
function raw_score_ajax() {

    if (!raw_score_loaded) {

        disable_inputs();

        // Get check box values for bar graph averages
        let T_AVG_BTN = $("#t_AVG:checked").val()
        let G_AVG_BTN = $("#g_AVG:checked").val()
        let P_AVG_BTN = $("#p_AVG:checked").val()

        // get dates from selectors
        let date_one = document.getElementById("date1")
        let date_two = document.getElementById("date2")

        resultone.innerText = date_one.options[date_one.selectedIndex].text;
        resulttwo.innerText = date_two.options[date_two.selectedIndex].text;

        // clear trends and graphs 
        $("#raw-score-graphs").empty()
        $("#test-list").empty()

        // add loading circle
        $("#bar-graphs").append("<div id=\"loading-bar\" class=\"d-flex justify-content-center\"> <div class=\"lds-dual-ring\"></div></div>");

        $.ajax({
            url: ajaxURL,
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
                req_type: "raw-score",
                date1: date_one.value,
                date2: date_two.value,
                T_AVG_BTN: T_AVG_BTN,
                G_AVG_BTN: G_AVG_BTN,
                P_AVG_BTN: P_AVG_BTN,
            }),
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            success: (response) => {

                //shows info being passed from backend
                console.log(response);

                //remove loading circle after info arrives from db
                $("#loading-bar").remove()

                //loop thru each test type and get its info
                for (let key in response.test_types) {

                    let bar_template = document.getElementById("bar-template").cloneNode(true);

                    // Construct URL for bar graph and add path to this node's img tag
                    let bar_graphURL = "data:image/png;base64, " + response.kpi_bar[key];
                    bar_template.querySelector("#tname").innerText = response.test_types[key];
                    bar_template.querySelector("#tgraph").setAttribute("src", bar_graphURL);

                    // Give both graphs for each type an integer ID that will allow them to be maniuplated later
                    bar_template.setAttribute("id", "bar_" + key);

                    // Add this completed graph template to the div containing all graphs
                    $("#raw-score-graphs").append(bar_template);

                    let checkid = /*"check_" +*/ key;

                    document.getElementById("test-list").innerHTML += "<li>" + response.test_types[key] + "<input type=\"checkbox\" id=\"" + checkid + "\" checked=\"true\"></li>";
                }
                raw_score_loaded = true;
                hide_tests();
                enable_inputs();
                
            },
            error: (error) => {
                console.log("Error processing KPI request: " + error);
            }
        })
    }
}


function trends_ajax() {

    // get dates from selectors
    let date_one = document.getElementById("date1")
    let date_two = document.getElementById("date2")

    resultone.innerText = date_one.options[date_one.selectedIndex].text;
    resulttwo.innerText = date_two.options[date_two.selectedIndex].text;

    // clear trends and graphs 
    $("#kpi-trend").empty()

    // add loading circle
    $("#kpi-trend").append("<div id=\"loading-line\" class=\"d-flex justify-content-center\"> <div class=\"lds-dual-ring\"></div></div>");

    $.ajax({
        url: ajaxURL,
        type: "POST",
        dataType: "json",
        data: JSON.stringify({
            req_type: "trend",
            date1: date_one.value,
            date2: date_two.value,
        }),
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        success: (response) => {

            //shows info being passed from backend
            console.log(response);

            //remove loading circle after info arrives from db
            $("#loading-line").remove()

            //loop thru each test type and get its info
            for (let key in response.test_types) {
                let trend_template = document.getElementById("trend-template").cloneNode(true);

                // If the change is increasing
                if (response.changes[key] > 0) {
                    // If a minimum score is better for a test, the change is increasing and is red
                    if (response.minBetter[key] === true)
                        trend_template.querySelector("#kpi-change").style.color = "var(--acc-color-neg)";
                    // If a minimum score is NOT better for a test, the change is increasing and is green
                    else if (response.minBetter[key] === false)
                        trend_template.querySelector("#kpi-change").style.color = "var(--acc-color-pos)";

                    // Add correctly oriented arrow icon
                    trend_template.querySelector("#kpi-arrow").setAttribute("class", "fa-solid fa-arrow-up");
                }
                // If the change is decreasing
                else if (response.changes[key] < 0) {
                    // If a minimum score is better for a test, the change is decreasing and is green
                    if (response.minBetter[key] === true)
                        trend_template.querySelector("#kpi-change").style.color = "var(--acc-color-pos)";
                    // If a minimum score is NOT better for a test, the change is decreasing and is red
                    else if (response.minBetter[key] === false)
                        trend_template.querySelector("#kpi-change").style.color = "var(--acc-color-neg)";

                    // Add correctly oriented arrow icon
                    trend_template.querySelector("#kpi-arrow").setAttribute("class", "fa-solid fa-arrow-down");
                }

                // Append the actual change value (in absolute form so there is no -)
                trend_template.querySelector("#kpi-change").append(Math.abs(response.changes[key]));

                // Construct URL for line graph and add path to this node's img tag
                let line_graphURL = "data:image/png;base64, " + response.kpi_line[key];
                trend_template.querySelector("#kpi-graph").setAttribute("src", line_graphURL);

                // Fill in name and dates for this KPI trend
                trend_template.querySelector("#kpi-name").innerText = response.test_types[key];
                trend_template.querySelector("#kpi-date-1").innerText = response.Date1_results[key];
                trend_template.querySelector("#kpi-date-2").innerText = response.Date2_results[key];

                // Give both graphs for each type an integer ID that will allow them to be maniuplated later
                trend_template.setAttribute("id", "trend_" + key);

                // Add this completed graph template to the div containing all graphs
                $("#kpi-trend").append(trend_template);
            }
            hide_tests();
        },
        error: (error) => {
            console.log("Error processing KPI Trends request: " + error);
        }
    })
}

//grabs info from the database without refreshing page and screwing everything up
function tscore_ajax() {

    if (!tscore_loaded) {

        disable_inputs();

        // Get radio button values for z-score graph varients
        let AVG_Radio_BTN = $(".radioBTN:checked").val();

        // get dates from selectors
        let date_one = document.getElementById("date1")
        let date_two = document.getElementById("date2")

        resultone.innerText = date_one.options[date_one.selectedIndex].text;
        resulttwo.innerText = date_two.options[date_two.selectedIndex].text;

        // clear trends and graphs 
        $("#t-score-graphs").empty()
        $("#test-list").empty()

        // add loading circle
        $("#t-score-graphs").append("<div id=\"loading-z\" class=\"d-flex justify-content-center\"> <div class=\"lds-dual-ring\"></div></div>");

        $.ajax({
            url: ajaxURL,
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
                req_type: "t-score",
                date1: date_one.value,
                date2: date_two.value,
                AVG_Radio_BTN: AVG_Radio_BTN,
            }),
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            success: (response) => {

                //shows info being passed from backend
                console.log(response);

                //remove loading circle after info arrives from db
                $("#loading-z").remove();

                //loop thru each test type and get its info
                for (let key in response.test_types) {

                    let z_template = document.getElementById("z-template").cloneNode(true);

                    // Construct URL for z-score graph and add path to this node's img tag
                    let z_graphURL = "data:image/png;base64, " + response.z_score_bar[key];
                    z_template.querySelector("#zname").innerText = response.test_types[key];
                    z_template.querySelector("#zgraph").setAttribute("src", z_graphURL);

                    // Give both graphs for each type an integer ID that will allow them to be maniuplated later
                    z_template.setAttribute("id", "z_" + key);

                    // Add this completed graph template to the div containing all graphs
                    $("#t-score-graphs").append(z_template);

                    let checkid = key;

                    document.getElementById("test-list").innerHTML += "<li>" + response.test_types[key] + "<input type=\"checkbox\" id=\"" + checkid + "\" checked=\"true\"></li>";
                }

                tscore_loaded = true;
                hide_tests();
                enable_inputs();
            },
            error: (error) => {
                console.log("Error processing T-Scores request: " + error);
            }
        })
    }
}
/* Wellness AJAX function */

/* When the "#wellnessform" form is submitted, this function will send an AJAX request to fetch the new data. */
function wellness_ajax() {
    // Get value of #wellnessdate
    let date_selected = document.getElementById("wellnessdate").value

    // Send "POST" AJAX request to url 'AthleteProf'
    // This request will be handled by the Django backend -> see views.py recordKPI() for that code
    $.ajax({
        //URL needs to be fname, lname, DOB for athletes
        url: ajaxURL,
        type: "POST",
        dataType: "json",
        data: JSON.stringify({
            req_type: "wellness",
            wellnessdate: date_selected,
        }),
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),  // don't forget to include the 'getCookie' function
        },
        success: (response) => {

            console.log(response);

            // Get individual values needed for wellness total and then sum them
            let hoursofsleep = Number(response.wellness[0].hoursofsleep);
            let sleepquality = Number(response.wellness[0].sleepquality);
            let breakfast = Number(response.wellness[0].breakfast);
            let hydration = Number(response.wellness[0].hydration);
            let soreness = Number(response.wellness[0].soreness);
            let stress = Number(response.wellness[0].stress);
            let mood = Number(response.wellness[0].mood);

            document.getElementById("hrs_sleep").innerText = hoursofsleep;
            document.getElementById("sleep_qual").innerText = sleepquality;
            document.getElementById("breakfast").innerText = breakfast;
            document.getElementById("hydration").innerText = hydration;
            document.getElementById("soreness").innerText = soreness;
            document.getElementById("stress").innerText = stress;
            document.getElementById("mood").innerText = mood;

            let total = hoursofsleep + sleepquality + breakfast + hydration + soreness + stress + mood;
            let status = response.wellness[0].status;

            // Update total & readiness in document
            document.getElementById("wellness_total").innerText = total;
            document.getElementById("stat").innerHTML = status;
            document.getElementById("total").innerHTML = "Readiness: " + total;

            if (status == "Out") {
                document.getElementById("stat-box").style.color = "var(--black-text)";
                document.getElementById("stat-box").style.backgroundColor = "var(--acc-color-neg)";
            }
            else if (status == "Good") {
                document.getElementById("stat-box").style.color = "var(--black-text)";
                document.getElementById("stat-box").style.backgroundColor = "var(--acc-color-pos)";
            }
        },
        error: (error) => {
            console.log(error);
            alert("Error processing Wellness request: " + error);
        }
    })
}

/* Miscellaneous functions */

// stops form from resubmitting when page is refreshed to show 
if (window.history.replaceState) {
    window.history.replaceState(null, null, window.location.href);
}

// submit the form to change database, and refresh the page to show new profile image       
function imgChange() {
    document.getElementById("imgForm").submit();
    document.getElementById("imgForm").reset();
}

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
                $("#trend_" + id).show();
                $("#z_" + id).show();
            }
            else {
                // concatenate respective ids of bar and trend graphs
                $("#bar_" + id).hide();
                $("#trend_" + id).hide();
                $("#z_" + id).hide();
            }
            e.stopPropagation();
        })
    })
}

function disable_inputs() {
    document.querySelectorAll("[type=checkbox]").forEach(checkbox => {
        checkbox.disabled = true;
    })
    document.querySelectorAll("select").forEach(select => {
        select.disabled = true;
    })
}
function enable_inputs() {
    document.querySelectorAll("[type=checkbox]").forEach(checkbox => {
        checkbox.disabled = false;
    })
    document.querySelectorAll("select").forEach(select => {
        select.disabled = false;
    })
}

//jQuery for functionality of "tabs"
$(document).ready(function () {

    //initially hide wellness report and show only kpi trends
    $("#wellnessreport").hide();
    document.getElementById("wellness-tab").style.backgroundColor = "var(--color-bg)";

    //initially hide spider graph, only show bar graph to begin with
    $("#bar-graphs").show();
    document.getElementById("spider-tab").style.backgroundColor = "var(--color-bg)";

    // initially show raw scores options in options card (since this will be the graphs that are shown first)
    $("#t-score-graphs").hide();
    $("#raw-score-graphs").show();

    $("#raw-score-selections").show();
    $("#t-score-selections").hide();

    //upon click of wellness tab, show wellnessreport div & hide kpireport div
    //swap color of tab
    $("#wellness-tab").click(function () {
        $("#kpireport").hide();
        $("#wellnessreport").show();
        document.getElementById("wellness-tab").style.backgroundColor = "var(--color-secondary)";
        document.getElementById("kpi-tab").style.backgroundColor = "var(--color-bg)";
    });

    //upon click of kpi tab, show kpireport div & hide wellnessreport div
    //swap color of tab
    $("#kpi-tab").click(function () {
        $("#kpireport").show();
        $("#wellnessreport").hide();
        $("#spider-date-div").hide();
        $("#kpi-dates-div").show();
        document.getElementById("kpi-tab").style.backgroundColor = "var(--color-secondary)";
        document.getElementById("wellness-tab").style.backgroundColor = "var(--color-bg)";
    });

    //upon click of spider-tab, show spider-graphs div & hide bar-graph div
    //swap color of tab
    $("#spider-tab").click(function () {
        $("#bar-graphs").hide();
        $("#spider-graphs").show();
        $("#spider-date-div").show();
        $("#kpi-dates-div").hide();
        document.getElementById("spider-tab").style.backgroundColor = "var(--color-secondary)";
        document.getElementById("bar-tab").style.backgroundColor = "var(--color-bg)";

        $("#t-score-selections").hide();
        $("#raw-score-selections").hide();
    });

    //upon click of bar-tab, show bar-graph  div & hide spider-graphs div
    //swap color of tab
    $("#bar-tab").click(function () {
        $("#spider-graphs").hide();
        $("#bar-graphs").show();
        $("#spider-date-div").hide();
        $("#kpi-dates-div").show();
        document.getElementById("bar-tab").style.backgroundColor = "var(--color-secondary)";
        document.getElementById("spider-tab").style.backgroundColor = "var(--color-bg)";

        $("#raw-score-selections").show();
        $("#t-score-selections").hide();

    });

    $("#t-score-radio").click(function () {
        $("#t-score-graphs").show();
        $("#raw-score-graphs").hide();

        $("#raw-score-selections").hide();
        $("#t-score-selections").show();

        if (!tscore_loaded)
            tscore_ajax();

    });

    $("#raw-score-radio").click(function () {
        $("#raw-score-graphs").show();
        $("#t-score-graphs").hide();

        $("#raw-score-selections").show();
        $("#t-score-selections").hide();

        if (!raw_score_loaded)
            raw_score_ajax();
    });

    // upon click of cog wheel "settings", show the options card
    // if it's already showing, close it. functions as a toggle
    $("#settings").click(function () {
        if ($('#options-card').is(':hidden')) {
            $("#options-card").show();
        } else {
            $("#options-card").hide();
        }

    });
});