document.addEventListener("DOMContentLoaded", () => {
    // language selector
    const el_language_selector = document.getElementById(
        "dropdown-language-selector",
    );
    el_language_selector.addEventListener("change", (e) => {
        const path_parts = window.location.pathname.split("/");
        path_parts[1] = e.target.value;
        window.location.href = window.location.origin + path_parts.join("/");
    });
});

let toggle = document.querySelector(".nav-toggle");
let navLeft = document.querySelector(".nav-links");

toggle?.addEventListener("click", () => {
    navLeft.classList.toggle("nav-open");
});
