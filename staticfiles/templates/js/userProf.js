document.addEventListener("DOMContentLoaded", function() {

    let fname_prof = window.userData.fname; 
    let lname_prof = window.userData.lname; 
    
    // Gets just the first character from first and last names 
    // Makes them uppercase
    let f_init_prof = fname_prof.charAt(0).toUpperCase();
    let l_init_prof = lname_prof.charAt(0).toUpperCase();
    
    // Injects initials and names into HTML
    document.getElementById("user-initials_profile").innerText = f_init_prof + l_init_prof;
    
    let rowCount = document.getElementById('usertable').rows.length;
    document.getElementById("userCount").innerHTML = "(" + rowCount + ")";

});
