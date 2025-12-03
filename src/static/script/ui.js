document.addEventListener("DOMContentLoaded", () => {
    // language selector
    const el_language_selector = document.getElementById(
        "dropdown-language-selector",
    );
    el_language_selector.addEventListener("change", (e) => {
        window.location.href = "/" + e.target.value;
    });
});
