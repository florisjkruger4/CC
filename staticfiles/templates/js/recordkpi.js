let recordKPI_Ajax_url, addTest_Ajax_url;
let today;

let columnCount, addcol;
let TestTypeArray = [], InputCellArray = [], ParentIDarray = [];
let sport_selected, date_selector;

/* Initial Page Load */
document.addEventListener("DOMContentLoaded", function () {

    recordKPI_Ajax_url = window.recordKPIdata.recordKPI_url;
    addTest_Ajax_url = window.recordKPIdata.addTestType_url;

    /* This block of code sets the default date in the selector to today's date */
    // Get today's date as a string in the format "yyyy-mm-dd"
    today = new Date().toISOString().substr(0, 10);
    document.getElementById("date_selector").value = today;

    date_selector = document.getElementById("date_selector").value

    // show "how to" message on page load
    // disable selection of checkboxes on page load
    document.getElementById("sportsteam").addEventListener("change", function (e) {
        $("#how-to").hide();
        document.querySelectorAll("[type=checkbox]").forEach(checkbox => {
            checkbox.disabled = false;
        })
    })

    //listen for updated checkbox input in list of test types
    //if checked, add a column to table
    //if unchecked, remove the column
    document.querySelectorAll("[type=checkbox]").forEach(checkbox => {
        checkbox.addEventListener("click", function (e) {
            id = this.id
            document.getElementById("submitbtn").onclick = function () {
            sendData(ParentIDarray, id)
            }
            document.getElementById("clearbtn").onclick = function () {
            clearTable(ParentIDarray)
            }
            viewArr(this.id)
            if (this.checked)
            addColumn(this.previousSibling.innerText, this.id);
            else
            deleteColumn(this.previousSibling.innerText, this.id, ParentIDarray);
            e.stopPropagation();
        })
    })

    // Variables to hold refrences to HTML elements
    const addTestBtn = document.getElementById('addTestBtn');
    const addTestForm = document.getElementById('addTestForm');
    const submitTestBtn = document.getElementById('submitTestBtn');
    const minBetter = document.getElementById('minBetter')
    const Tname = document.getElementById('Tname')

    // Event listener to show and hide the form
    addTestBtn.addEventListener('click', () => {
        if (addTestForm.style.display === 'none') {
        addTestForm.style.display = 'block'; // Show the addTestForm
        addTestBtn.textContent = 'Close';
        } else {
        addTestForm.style.display = 'none'; // Hide the addTestForm
        addTestBtn.textContent = 'Add New Test';
        }
    });

    // Event listener for addTestBtn to submit/add a new test
    submitTestBtn.addEventListener('click', (event) => {
        // Prevent the default addTestForm submission behavior
        event.preventDefault(); // Prevent default addTestForm submission behavior

        // Variable to hold the addTestForm data
        const data = {
            Tname: Tname.value,
            minBetter: minBetter.checked
        };

        //add loading circle
        $("#header").append("<div id=\"loading\" class=\"lds-dual-ring-small\"></div>");

        $.ajax({
        // URL to send the AJAX request to
        url: addTest_Ajax_url,
        // HTTP method used to send the request
        type: "POST",
        // Type of data expected in the response
        dataType: "json",
        // Data to be sent with the request, in this case a JSON object converted to a string
        data: JSON.stringify(data),
        headers: {
            // Header to identify the request as an AJAX request
            "X-Requested-With": "XMLHttpRequest",
            // Header with the CSRF token
            "X-CSRFToken": getCookie("csrftoken"),
            // Header indicating that the data sent with the request is in JSON format
            "Content-Type": "application/json"
        },
        success: (response) => {
            $("#loading").remove();
            
            console.log(response);
            // Display a success message
            alert("Test added successfully");
            // Clear the addTestForm
            addTestForm.reset();
            // Hide the addTestForm
            addTestForm.style.display = 'none';
            addTestBtn.textContent = 'Add New Test';
        },
        // Error handling
        error: (error) => {
            console.log(error);
            // Display an error message
            alert("Error adding test");
        }
        });
    });
});

function listFilter() {
// Declare variables
    var input, filter, ul, li, a, i, txtValue;
    input = document.getElementById('test-search');
    filter = input.value.toUpperCase();
    ul = document.getElementById("test-list");
    li = ul.getElementsByTagName('li');

    // Loop through all list items, and hide those who don't match the search query
    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName("a")[0];
        txtValue = a.textContent || a.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1)
        li[i].style.display = "";
        else
        li[i].style.display = "none";

    }
}

//add a column to the table with new test type as header and 
//input boxes for each athlete
function addColumn(value, id) {

    var tblHeadObj = document.getElementById("data-table").tHead;

    for (var h = 0; h < tblHeadObj.rows.length; h++) {
        var newTH = document.createElement('th');

        //attach id of test type from list to this header cell so that it
        //can be removed/tracked later
        newTH.setAttribute('id', id);
        tblHeadObj.rows[h].appendChild(newTH);
        newTH.innerHTML = value;

        // add testtype to array
        TestTypeArray.push(value)
    }

    var tblBodyObj = document.getElementById("data-table").tBodies[0];

    for (var i = 0; i < tblBodyObj.rows.length; i++) {
        var newCell = tblBodyObj.rows[i].insertCell(-1);
        //attach id of test type from list to this body cell so that it
        //can be removed/tracked later

        // newcell parent element id
        parentID = newCell.parentElement.id
        newCell.setAttribute('id', id);

        // populates parent id array
        ParentIDarray.push(id + parentID)

        //add text field input to cell
        newCell.innerHTML = "<input class=\"form-control input-box i-size\" type=\"text\" id=" + id + parentID + "></input>";
    }

    console.log('test type arr: ' + TestTypeArray)
    console.log('parent arr: ' + ParentIDarray)

}

//deletes a column when test type is unchecked
function deleteColumn(value, id, ParentIDarray) {

    var table = tblHeadObj = document.getElementById("data-table").rows
    var rows = table.length - 1;

    // find index of testype wanting to be removed
    var index = TestTypeArray.indexOf(value)
    // remove that index using splice
    if (index > -1) { // only splice array when item is found
        TestTypeArray.splice(index, 1); // 2nd parameter means remove one item only
        
        var athlete_indexes = (index * rows);

        var p_index = ParentIDarray.indexOf(ParentIDarray[athlete_indexes]);
        console.log("p_index: " + p_index);
        ParentIDarray.splice(p_index, rows);

        console.log('parent arr AFTER: ' + ParentIDarray)
        
    }

    //find all headers with desired id and remove
    $("#data-table").find("th#" + id).remove();

    //find all cells with desired id and remove
    $("#data-table").find("td#" + id).remove();

    console.log("index: " + index)
    console.log('test type arr: ' + TestTypeArray)
    
}

function sendData(ParentIDarray, id) {
    for (var i = 0; i < ParentIDarray.length; i++) {
        x = document.getElementById(ParentIDarray[i]).value
        if (!x) {
        x = "-1"
        }
        console.log("id of cell: " + ParentIDarray[i] + ", value of cell: " + x)
        InputCellArray.push(x)
    }

    console.log('test type arr: ' + TestTypeArray)
    console.log('input cell array: ' + InputCellArray)
    console.log("parent array value: " + ParentIDarray)

    viewArr(id, InputCellArray)
    //alert("data logged successfully")

    clearTable(ParentIDarray)

}

function clearTable(ParentIDarray) {
    for (var i = 0; i < ParentIDarray.length; i++) {
        x = document.getElementById(ParentIDarray[i]).value = ""
        //InputCellArray.push(x)
    }
    // empty out array
    InputCellArray = []
    console.log('test type arr: ' + TestTypeArray)
    console.log('input cell array: ' + InputCellArray)
    console.log('parent arr: ' + ParentIDarray)
}

function viewArr(id, InputCellArray) {
    //console.log(id)
    $.ajax({
        url: recordKPI_Ajax_url,
        type: "POST",
        dataType: "json",
        data: JSON.stringify({
        TestTypeArray: TestTypeArray,
        InputCellArray: InputCellArray,
        sportsteam: sport_selected,
        date_selector: date_selector,
        }),
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),  // don't forget to include the 'getCookie' function
        },
        success: (response) => {
        //console.log(response);
        if (InputCellArray.length != 0) {
            alert("data logged successfully")
        }
        },
            error: (error) => {
            alert("Conflicting KPI Date Selected... Please Select a Different Date");
        }
    })
}

/* When the "#sportsteam" form is changed, this function will send an AJAX request to fetch the new team data. */
// When for "#sportsteam" is changed...

//jQuery for functionality of "tabs"
$(document).ready(function () {
    $("#sportsteam").change(function (event) {

        // Get value of #sportsteam
        var sport_selected = document.getElementById("sportsteam").value

        $.ajax({
            url: recordKPI_Ajax_url,
            type: "POST",
            dataType: "json",
            data: JSON.stringify({ sportsteam: sport_selected, }),
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": getCookie("csrftoken"),  // don't forget to include the 'getCookie' function
            },
            success: (response) => {
                $("#hide").show();
                $("#tvalues").empty();
                for (var key in response.athletes) {
                    var id = response.athletes[key].fname + response.athletes[key].lname + response.athletes[key].dob;
                    var athlete = response.athletes[key].fname + " " + response.athletes[key].lname;
                    var html = "<tr id=" + id + " ><td>" + athlete + "</td></tr>";
                    $("#tvalues").append(html);
                }
            },
            error: (error) => {
                alert(error);
            }
        })
    });
    // get sports team selected
    $("#sportsteam").change(function (event) {
        // Get value of #sportsteam
        sport_selected = document.getElementById("sportsteam").value
    });
    // get date selected
    $("#date_selector").change(function (event) {
        // Get value of #date-selector
        date_selector = document.getElementById("date_selector").value
    });
});