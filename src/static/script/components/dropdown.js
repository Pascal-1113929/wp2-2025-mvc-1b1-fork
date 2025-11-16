export default function initComponent() {
    const el_buttons = document.querySelectorAll(".dropdown-button");
    if (el_buttons.length === 0) return;

    el_buttons.forEach((el_button) => {
        const el_dropdown_select = el_button.closest(".dropdown-select");
        if (!el_dropdown_select) return;

        const el_hidden_select = el_dropdown_select.querySelector(
            ".dropdown-hidden-select",
        );
        const el_options =
            el_dropdown_select.querySelectorAll(".dropdown-option");

        el_button.addEventListener("click", () => {
            const is_open = el_dropdown_select.classList.toggle("open");
            el_button.setAttribute("aria-expanded", is_open);
        });

        el_options.forEach((el_option) => {
            el_option.addEventListener("click", () => {
                const value = el_option.getAttribute("value");
                const text = el_option.querySelector("span").textContent;
                const image = el_option.querySelector(".dropdown-image");

                el_hidden_select.value = value;

                el_button.innerHTML = "";
                if (image) {
                    const newImage = image.cloneNode(true);
                    el_button.appendChild(newImage);
                }
                const textSpan = document.createElement("span");
                textSpan.textContent = text;
                el_button.appendChild(textSpan);

                el_dropdown_select.classList.remove("open");
                el_button.setAttribute("aria-expanded", "false");
            });
        });

        document.addEventListener("click", (e) => {
            if (
                !el_dropdown_select.contains(e.target) &&
                !el_button.contains(e.target)
            ) {
                el_dropdown_select.classList.remove("open");
                el_button.setAttribute("aria-expanded", "false");
            }
        });

        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape") {
                el_dropdown_select.classList.remove("open");
                el_button.setAttribute("aria-expanded", "false");
                el_button.focus();
            }
        });
    });
}
