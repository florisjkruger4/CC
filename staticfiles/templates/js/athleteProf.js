/* Global variable declaration for current athlete's information */
let a_fname, a_lname, a_dob, a_id, kpi_count, wellness_count, kpi_earliest, all_dates;
let ajaxURL;
let tscore_loaded, raw_score_loaded;
let tscore_loading, raw_score_loading;
let graph_type_selected;

// Global variables for dates
let date_one;
let date_two;
let today;

let date_selector_type;

/* Initial Page Load */
document.addEventListener("DOMContentLoaded", function () {
    // initialize athlete data
    a_fname = window.athleteData.fname;
    a_lname = window.athleteData.lname;
    a_dob = window.athleteData.dob;
    a_id = window.athleteData.id;
    kpi_count = window.athleteData.kpi_count;
    wellness_count = window.athleteData.wellness_count;
    kpi_earliest = window.athleteData.kpi_earliest;
    all_dates = window.athleteData.all_dates;

    // initialize "lock" variables
    tscore_loaded = false, raw_score_loaded = false;
    tscore_loading = false, raw_score_loading = false;
    graph_type_selected = "rawscore";
    date_selector_type = "cal";

    // assemble AJAX URL
    // this will be used by all AJAX functions and doesn't change
    ajaxURL = "/" + a_fname + "/" + a_lname + "/" + a_dob + "/" + a_id;

    // get today's date
    today = new Date().toISOString().substr(0, 10);

    // set initial values for date selectors
    document.getElementById("cal-date1").value = kpi_earliest;
    document.getElementById("cal-date2").value = today;
    document.getElementById("exact-date1").value = all_dates[0];
    document.getElementById("exact-date2").value = all_dates[all_dates.length-1];

    // set min and max values for calendar selector so the user can only use
    // dates within a certain range (which is the first recorded kpi -> today)
    document.getElementById("cal-date1").max = today;
    document.getElementById("cal-date2").max = today;
    document.getElementById("cal-date1").min = all_dates[0];
    document.getElementById("cal-date2").min = all_dates[0];

    // initialize date_one and date_two
    // these will hold the current date selections for both selectors & are used
    // for ajax requests
    date_one = kpi_earliest;
    date_two = today;

    // spider graph date stuff. same as above
    spider_date = today;
    document.getElementById("spider_date").value = today;
    document.getElementById("spider_date").min = all_dates[0];
    document.getElementById("spider_date").max = today;

    // if there is at least 1 kpi report, submit ajax request to load raw score bar graphs
    // and trend reports
    if (kpi_count > 0) {
        raw_score_loaded = false;
        tscore_loaded = false;

        raw_score_ajax();
        trends_ajax();
    }

    // if there is at least 1 wellness report, submit ajax request to load most
    // recent wellness report
    if (wellness_count > 0)
        wellness_ajax();

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

// handles when user selects a date
function update_dates() {

    // get dates from selectors (depending on which is being used)
    if(date_selector_type = "cal") {
        date_one = document.getElementById("cal-date1").value;
        date_two = document.getElementById("cal-date2").value;
    }
    else if(date_selector_type = "exact"){
        date_one = document.getElementById("exact-date1").value;
        date_two = document.getElementById("exact-date2").value;
    }

    // if there are 2 dates selected, proceed
    if(date_one && date_two) {
        raw_score_loaded = false;
        tscore_loaded = false;

        if(graph_type_selected == "rawscore") {
            raw_score_ajax();
            trends_ajax();
        }
        else if(graph_type_selected == "tscore") {
            tscore_ajax();
            trends_ajax();
        }
    }
}

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

    // section is loading; don't allow user input while loading!
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
            alert("Error processing Spider Graph AJAX Request: " + error);
        }
    })
}

/* Raw Score & Trend Graph AJAX function */

//grabs info from the database without refreshing page and screwing everything up
function raw_score_ajax() {

    // this section is NOT up to date and is currently NOT loading, so a request is allowed
    if (!raw_score_loaded && !raw_score_loading) {

        // Get check box values for bar graph averages
        let T_AVG_BTN = $("#t_AVG:checked").val()
        let G_AVG_BTN = $("#g_AVG:checked").val()
        let P_AVG_BTN = $("#p_AVG:checked").val()

        // clear trends and graphs 
        $("#raw-score-graphs").empty()
        $("#test-list").empty()

        // add loading circle
        $("#raw-score-graphs").append("<div id=\"loading-raw-score\" class=\"d-flex justify-content-center\"> <div class=\"lds-dual-ring\"></div></div>");

        // section is loading; don't allow user input while loading!
        raw_score_loading = true;
        disable_inputs();

        $.ajax({
            url: ajaxURL,
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
                req_type: "raw-score",
                date1: date_one,
                date2: date_two,
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
                $("#loading-raw-score").remove()

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

                    // add this test to list of test types within settings (option card)
                    let checkid = key;
                    document.getElementById("test-list").innerHTML += "<li>" + response.test_types[key] + "<input type=\"checkbox\" id=\"" + checkid + "\" checked=\"true\"></li>";

                    // section IS loaded
                    // section is no longer loading
                    // give display test options back 
                    // enable inputs
                    raw_score_loaded = true;
                    raw_score_loading = false;
                    hide_tests();
                    enable_inputs();
                }
                
            },
            error: (error) => {
                alert("Error processing Bar Graph (Raw Scores) AJAX Request: " + error);

                // section IS loaded
                // section is no longer loading
                // give display test options back 
                // enable inputs
                raw_score_loaded = true;
                raw_score_loading = false;
                hide_tests();
                enable_inputs();
            }
        })
    }
}

/* T-Score AJAX Function */
function tscore_ajax() {

    // this section is NOT up to date and is currently NOT loading, so a request is allowed
    if (!tscore_loaded && !tscore_loading) {

        // Get radio button values for z-score graph varients
        let AVG_Radio_BTN = $(".radioBTN:checked").val();

        // clear trends and graphs 
        $("#t-score-graphs").empty()
        $("#test-list").empty()

        // add loading circle
        $("#t-score-graphs").append("<div id=\"loading-t\" class=\"d-flex justify-content-center\"> <div class=\"lds-dual-ring\"></div></div>");

        // section is loading; don't allow user input while loading!
        tscore_loading = true;
        disable_inputs();

        $.ajax({
            url: ajaxURL,
            type: "POST",
            dataType: "json",
            data: JSON.stringify({
                req_type: "t-score",
                date1: date_one,
                date2: date_two,
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
                $("#loading-t").remove();

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

                    // add this test to list of test types within settings (option card)
                    let checkid = key;
                    document.getElementById("test-list").innerHTML += "<li>" + response.test_types[key] + "<input type=\"checkbox\" id=\"" + checkid + "\" checked=\"true\"></li>";

                    // section IS loaded
                    // section is no longer loading
                    // give display test options back 
                    // enable inputs
                    tscore_loaded = true;
                    tscore_loading = false;
                    hide_tests();
                    enable_inputs();
                }
            },
            error: (error) => {
                alert("Error processing Bar Graph (T-Scores) AJAX Request: " + error);

                // section IS loaded
                // section is no longer loading
                // give display test options back 
                // enable inputs
                tscore_loaded = true;
                tscore_loading = false;
                hide_tests();
                enable_inputs();
            }
        })

    }
}

/* Trends AJAX function */
function trends_ajax() {

    resultone.innerText = date_one;
    resulttwo.innerText = date_two;

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
            date1: date_one,
            date2: date_two,
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
            alert("Error processing KPI Trend AJAX Request: " + error);
        }
    })
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

            // depending on status, change bg color of "stat-box" to either red for out, or green for good
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

    // if wellness "tab" is clicked...
    $("#wellness-tab").click(function () {
        // hide kpi report & show wellness report
        $("#kpireport").hide();
        $("#wellnessreport").show();
        
        // change color of tabs
        document.getElementById("wellness-tab").style.backgroundColor = "var(--color-secondary)";
        document.getElementById("kpi-tab").style.backgroundColor = "var(--color-bg)";
    });

    // if kpi "tab" is clicked...
    $("#kpi-tab").click(function () {
        // hide wellness report and show kpi report
        $("#kpireport").show();
        $("#wellnessreport").hide();

        //change color of tabs
        document.getElementById("kpi-tab").style.backgroundColor = "var(--color-secondary)";
        document.getElementById("wellness-tab").style.backgroundColor = "var(--color-bg)";
    });

    // if spider graph "tab" is clicked...
    $("#spider-tab").click(function () {
        // hide bar graphs and show spider graph
        $("#bar-graphs").hide();
        $("#spider-graphs").show();

        // display spider graph date input & hide bar graph date input
        $("#spider-date-div").show();
        $("#kpi-dates-div").hide();

        // change color of tabs
        document.getElementById("spider-tab").style.backgroundColor = "var(--color-secondary)";
        document.getElementById("bar-tab").style.backgroundColor = "var(--color-bg)";

        // hide raw score and t-score settings (option card)
        $("#t-score-selections").hide();
        $("#raw-score-selections").hide();
    });

    // if bar graph "tab" is clicked...
    $("#bar-tab").click(function () {
        // show bar graphs and hide spider graph
        $("#spider-graphs").hide();
        $("#bar-graphs").show();

        // display bar graph date input & hide spider graph date input
        $("#spider-date-div").hide();
        $("#kpi-dates-div").show();

        // change color of tabs
        document.getElementById("bar-tab").style.backgroundColor = "var(--color-secondary)";
        document.getElementById("spider-tab").style.backgroundColor = "var(--color-bg)";

        // change settings (option card) depending on current bar graph type selection
        if(graph_type_selected == "rawscore") {
            $("#raw-score-selections").show();
            $("#t-score-selections").hide();
        }
        else if(graph_type_selected == "tscore") {
            $("#raw-score-selections").hide();
            $("#t-score-selections").show();
        }
    });

    // if "T" button is clicked...
    $("#t-score-radio").click(function () {
        // show t-score graphs and hide raw score graphs
        $("#t-score-graphs").show();
        $("#raw-score-graphs").hide();

        // change settings (option card)
        $("#raw-score-selections").hide();
        $("#t-score-selections").show();

        // tscore graph has been selected
        graph_type_selected = "tscore";

        // if this button is clicked and tscore has NOT yet been loaded, load it
        // otherwise, don't waste time rendering it again (because none of the inputs have changed)
        if (!tscore_loaded)
            tscore_ajax();

    });

    // if "R" button is clicked...
    $("#raw-score-radio").click(function () {
        // show raw score graphs and hide t-score graphs
        $("#raw-score-graphs").show();
        $("#t-score-graphs").hide();

        // change settings (option card)
        $("#raw-score-selections").show();
        $("#t-score-selections").hide();

        // raw score graph has been selected
        graph_type_selected = "rawscore";

        // if this button is clicked and raw score has NOT yet been loaded, load it
        // otherwise, don't waste time rendering it again (because none of the inputs have changed)
        if (!raw_score_loaded)
            raw_score_ajax();
    });

    // toggle for calendar/selector date input
    $("#cal-toggle").click(function () {
        if ($('#exact-date').is(':hidden')) {
            $("#exact-date").show();
            $("#cal-date").hide();
            date_selector_type =  "exact";
        } else {
            $("#cal-date").show();
            $("#exact-date").hide();
            date_selector_type = "cal";
        }
    });
});