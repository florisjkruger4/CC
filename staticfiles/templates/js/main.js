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