document.addEventListener("DOMContentLoaded", () => {
  const toggle = document.querySelector(".ai-assistant-menu-toggle");
  const sidebar = document.getElementById("ai-assistant-sidebar");
  const backdrop = document.getElementById("ai-assistant-backdrop");
  const closeButton = document.querySelector(".ai-assistant-menu-close");

  if (!toggle || !sidebar || !backdrop || !closeButton) return;

  const closeMenu = () => {
    sidebar.classList.remove("is-open");
    sidebar.setAttribute("aria-hidden", "true");
    toggle.setAttribute("aria-expanded", "false");
    backdrop.hidden = true;
    document.body.classList.remove("ai-assistant-menu-open");
  };

  const openMenu = () => {
    sidebar.classList.add("is-open");
    sidebar.setAttribute("aria-hidden", "false");
    toggle.setAttribute("aria-expanded", "true");
    backdrop.hidden = false;
    document.body.classList.add("ai-assistant-menu-open");
    closeButton.focus();
  };

  toggle.addEventListener("click", () => {
    if (toggle.getAttribute("aria-expanded") === "true") {
      closeMenu();
    } else {
      openMenu();
    }
  });
  closeButton.addEventListener("click", closeMenu);
  backdrop.addEventListener("click", closeMenu);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
      closeMenu();
      toggle.focus();
    }
  });
  sidebar.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeMenu));
});
