/* Toggle between showing and hiding the navigation menu links when the user clicks on the hamburger menu / bar icon */
function toggleMenu() {
    var x = document.getElementById("myLinks");
    if (x.style.display === "block") {
        x.style.display = "none";
        x.previousElementSibling.classList.remove("opened");
    } else {
        x.style.display = "block";
        x.previousElementSibling.classList.add("opened");
    }
}

/* Toggle loader */
function showLoader() {
    document.getElementById('loader-container').style.display = 'flex';
}

function hideLoader() {
    document.getElementById('loader-container').style.display = 'none';
}