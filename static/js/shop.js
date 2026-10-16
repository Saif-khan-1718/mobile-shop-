(function () {
    var toggle = document.querySelector(".menu-toggle");
    var header = document.querySelector(".header-inner");
    if (!toggle || !header) {
        return;
    }

    toggle.addEventListener("click", function () {
        var open = header.classList.toggle("is-open");
        document.body.classList.toggle("nav-open", open);
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
        toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
})();
