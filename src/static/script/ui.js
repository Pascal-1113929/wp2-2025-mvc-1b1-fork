import Dropdown from "./components/dropdown.js";

document.addEventListener("DOMContentLoaded", () => {
    // initialize components
    Dropdown();

    // language selector
    const el_language_selector = document.getElementById(
        "dropdown-language-selector",
    );
    el_language_selector.addEventListener("change", (e) => {
        console.log(e);
    });

    // TODO: omdat de change event niet getriggerd wordt moeten we een custom event aanmaken
});
