const welcomeButton = document.getElementById("welcomeButton");

if (welcomeButton) {
    welcomeButton.addEventListener("click", function () {
        alert("Welcome to StudentHub!");
    });
}

document.querySelectorAll(".progress-bar-fill[data-width]").forEach(function (bar) {
    bar.style.width = `${bar.dataset.width}%`;
});
