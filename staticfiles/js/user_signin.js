function toastFunction() {
    var x = document.getElementById("toast");
    x.classList.add("show");
    setTimeout(function(){ x.classList = x.classList.remove("show"); }, 7800);
}