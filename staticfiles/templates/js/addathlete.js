document.addEventListener("DOMContentLoaded", function() {
    // Prevents form resubmit when page is refreshed
    if ( window.history.replaceState ) {
        window.history.replaceState( null, null, window.location.href );
    }
});

function loadPage() {
    document.getElementById("addForm").reset();
}

function fileUpload() {
    if(document.getElementById("id_image").files.length > 0 ){
    document.getElementById("imgHolder").style.backgroundColor = "var(--light-gray-1)";
    document.getElementById("camicon").style.color = "var(--dark-gray)";
    document.getElementById("uploadmsg").style.visibility = "visible";
    }
}