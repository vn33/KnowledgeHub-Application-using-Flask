const themeToggleBtn = document.getElementById("theme-toggle");

function enableDarkmode() {
    document.documentElement.classList.add("darkmode");
    localStorage.setItem('darkmode', 'active');
    themeToggleBtn.innerHTML = "☾⋆"; 
}

function disableDarkmode() {
    document.documentElement.classList.remove("darkmode");
    localStorage.setItem('darkmode', 'inactive');
    themeToggleBtn.innerHTML = "☼";
}

themeToggleBtn.addEventListener("click", () => {
    const currentState = localStorage.getItem('darkmode');
    if (currentState !== "active") {
        enableDarkmode();
    } else {
        disableDarkmode();
    }
});
