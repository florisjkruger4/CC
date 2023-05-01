document.addEventListener("DOMContentLoaded", function() {

    const fname = window.nav_userData.fname; 
    const lname = window.nav_userData.lname; 

    // Formats first name with uppercase first letter
    form_fname = fname.charAt(0).toUpperCase() + fname.slice(1);

    // Gets just the first character from first and last names 
    // Makes them uppercase
    var f_init = fname.charAt(0).toUpperCase();
    var l_init = lname.charAt(0).toUpperCase();

    // Injects initials and names into HTML
    document.getElementById("user-initials").innerText = f_init + l_init;
    document.getElementById("username").innerText = form_fname + " " + l_init + ".";

});