/**
 * ui.js - Shared UI components for CareerHub (Toast, Loading/Empty/Error states, Mobile Nav Drawer)
 */
(function (global) {
  "use strict";

  const TOAST_ICONS = {
    success: "✓",
    error: "!",
    warning: "⚠",
    info: "i",
  };

  function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function ensureToastContainer() {
    let container = document.getElementById("ch-toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "ch-toast-container";
      container.className = "ch-toast-container";
      container.setAttribute("aria-live", "polite");
      container.setAttribute("aria-atomic", "false");
      document.body.appendChild(container);
    }
    return container;
  }

  function showToast(arg1, arg2, arg3) {
    if (!document.body) {
      document.addEventListener("DOMContentLoaded", () => showToast(arg1, arg2, arg3), { once: true });
      return;
    }

    let title = "";
    let message = "";
    let type = "info";
    let duration = 3800;

    if (arg1 && typeof arg1 === "object") {
      title = arg1.title || "";
      message = arg1.message || "";
      type = arg1.type || "info";
      if (typeof arg1.duration === "number") duration = arg1.duration;
    } else if (typeof arg3 === "boolean") {
      title = String(arg1 || "");
      message = String(arg2 || "");
      type = arg3 ? "error" : "success";
    } else if (arg2 && ["success", "error", "warning", "info"].includes(String(arg2))) {
      message = String(arg1 || "");
      type = String(arg2);
    } else if (arg2 !== undefined && arg2 !== null && String(arg2) !== "") {
      title = String(arg1 || "");
      message = String(arg2 || "");
      type = "success";
    } else {
      message = String(arg1 || "");
      type = "info";
    }

    const container = ensureToastContainer();
    const toast = document.createElement("div");
    toast.className = `ch-toast ch-toast--${type}`;
    toast.setAttribute("role", type === "error" ? "alert" : "status");

    const iconWrap = document.createElement("span");
    iconWrap.className = "ch-toast__icon";
    iconWrap.setAttribute("aria-hidden", "true");
    iconWrap.textContent = TOAST_ICONS[type] || TOAST_ICONS.info;

    const body = document.createElement("div");
    body.className = "ch-toast__body";

    if (title) {
      const titleEl = document.createElement("strong");
      titleEl.className = "ch-toast__title";
      titleEl.textContent = title;
      body.appendChild(titleEl);
    }

    if (message) {
      const msgEl = document.createElement("p");
      msgEl.className = "ch-toast__message";
      msgEl.textContent = message;
      body.appendChild(msgEl);
    }

    const closeBtn = document.createElement("button");
    closeBtn.type = "button";
    closeBtn.className = "ch-toast__close";
    closeBtn.setAttribute("aria-label", "Đóng thông báo");
    closeBtn.textContent = "×";

    const removeToast = () => {
      toast.classList.remove("is-visible");
      window.setTimeout(() => toast.remove(), 220);
    };

    closeBtn.addEventListener("click", removeToast);
    toast.append(iconWrap, body, closeBtn);
    container.appendChild(toast);

    while (container.children.length > 4) {
      container.firstElementChild.remove();
    }

    requestAnimationFrame(() => toast.classList.add("is-visible"));
    if (duration > 0) window.setTimeout(removeToast, duration);
    return toast;
  }

  function renderLoading(target, message = "Đang tải dữ liệu...") {
    const el = typeof target === "string" ? document.getElementById(target) : target;
    if (!el) return;
    el.innerHTML = `
      <div class="ui-state ui-state--loading" role="status" aria-live="polite">
        <div class="ui-spinner" aria-hidden="true"></div>
        <p class="ui-state__desc">${escapeHtml(message)}</p>
      </div>
    `;
  }

  function renderEmpty(target, options = {}) {
    const el = typeof target === "string" ? document.getElementById(target) : target;
    if (!el) return;
    const {
      icon = "📂",
      title = "Chưa có dữ liệu",
      message = "Hiện chưa có nội dung phù hợp để hiển thị.",
      actionLabel = "",
      actionHref = "",
      onAction = null,
    } = options;

    const wrap = document.createElement("div");
    wrap.className = "ui-state ui-state--empty";

    const iconEl = document.createElement("div");
    iconEl.className = "ui-state__icon";
    iconEl.setAttribute("aria-hidden", "true");
    iconEl.textContent = icon;

    const titleEl = document.createElement("h3");
    titleEl.className = "ui-state__title";
    titleEl.textContent = title;

    const descEl = document.createElement("p");
    descEl.className = "ui-state__desc";
    descEl.textContent = message;

    wrap.append(iconEl, titleEl, descEl);

    if (actionLabel) {
      if (actionHref) {
        const link = document.createElement("a");
        link.className = "btn btn-outline ui-state__action";
        link.href = actionHref;
        link.textContent = actionLabel;
        wrap.appendChild(link);
      } else if (typeof onAction === "function") {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "btn btn-outline ui-state__action";
        btn.textContent = actionLabel;
        btn.addEventListener("click", onAction);
        wrap.appendChild(btn);
      }
    }

    el.replaceChildren(wrap);
  }

  function renderError(target, options = {}) {
    const el = typeof target === "string" ? document.getElementById(target) : target;
    if (!el) return;
    const {
      title = "Không thể tải dữ liệu",
      message = "Đã xảy ra lỗi kết nối. Vui lòng thử lại sau.",
      retryLabel = "Thử lại",
      onRetry = null,
    } = options;

    const wrap = document.createElement("div");
    wrap.className = "ui-state ui-state--error";
    wrap.setAttribute("role", "alert");

    const iconEl = document.createElement("div");
    iconEl.className = "ui-state__icon";
    iconEl.setAttribute("aria-hidden", "true");
    iconEl.textContent = "!";

    const titleEl = document.createElement("h3");
    titleEl.className = "ui-state__title";
    titleEl.textContent = title;

    const descEl = document.createElement("p");
    descEl.className = "ui-state__desc";
    descEl.textContent = message;

    wrap.append(iconEl, titleEl, descEl);

    if (typeof onRetry === "function") {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn btn-primary ui-state__action";
      btn.textContent = retryLabel;
      btn.addEventListener("click", onRetry);
      wrap.appendChild(btn);
    }

    el.replaceChildren(wrap);
  }

  function initMobileNav() {
    const header = document.querySelector(".site-header");
    if (!header) return;
    const navbar = header.querySelector(".site-navbar");
    if (!navbar) return;

    const menuLinks = Array.from(navbar.querySelectorAll(".nav-menu a"));
    if (menuLinks.length === 0) return;

    let toggleBtn = navbar.querySelector(".nav-toggle");
    if (!toggleBtn) {
      toggleBtn = document.createElement("button");
      toggleBtn.type = "button";
      toggleBtn.className = "nav-toggle";
      toggleBtn.setAttribute("aria-label", "Mở menu điều hướng");
      toggleBtn.setAttribute("aria-expanded", "false");
      toggleBtn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <line x1="3" y1="6" x2="21" y2="6"></line>
          <line x1="3" y1="12" x2="21" y2="12"></line>
          <line x1="3" y1="18" x2="21" y2="18"></line>
        </svg>
      `;
      navbar.appendChild(toggleBtn);
    }

    let backdrop = document.getElementById("mobile-nav-backdrop");
    if (!backdrop) {
      backdrop = document.createElement("div");
      backdrop.id = "mobile-nav-backdrop";
      backdrop.className = "mobile-nav-backdrop";
      document.body.appendChild(backdrop);
    }

    let drawer = document.getElementById("mobile-nav-drawer");
    if (!drawer) {
      drawer = document.createElement("aside");
      drawer.id = "mobile-nav-drawer";
      drawer.className = "mobile-nav-drawer";
      drawer.setAttribute("aria-label", "Menu điều hướng di động");
      drawer.setAttribute("aria-hidden", "true");
      document.body.appendChild(drawer);
    }

    const renderDrawer = () => {
      const linksHtml = menuLinks
        .map((a) => {
          const active = a.classList.contains("active") ? " active" : "";
          return `<a href="${escapeHtml(a.getAttribute("href") || "#")}" class="mobile-nav-link${active}">${escapeHtml(a.textContent.trim())}</a>`;
        })
        .join("");

      const user = typeof AuthGuard !== "undefined" ? AuthGuard.getUser() : null;
      let actionsHtml = "";
      if (user) {
        const profileUrl =
          user.role === "student"
            ? "/profile.html"
            : user.role === "employer"
              ? "/employer_profile.html"
              : "/admin_dashboard.html";
        actionsHtml = `
          <div class="mobile-nav-actions">
            <a href="${profileUrl}" class="btn btn-outline">Hồ sơ cá nhân</a>
            <button type="button" class="btn btn-primary" id="mobile-nav-logout">Đăng xuất</button>
          </div>
        `;
      } else {
        actionsHtml = `
          <div class="mobile-nav-actions">
            <a href="/login.html" class="btn btn-outline">Đăng nhập</a>
            <a href="/register.html" class="btn btn-primary">Đăng ký</a>
          </div>
        `;
      }

      drawer.innerHTML = `
        <div class="mobile-nav-header">
          <a href="/home.html" class="brand-logo" title="CareerHub">
            <img src="/logoCHT-Photoroom.png" alt="CareerHub Logo" />
          </a>
          <button type="button" class="mobile-nav-close" aria-label="Đóng menu">&times;</button>
        </div>
        <nav class="mobile-nav-links">${linksHtml}</nav>
        ${actionsHtml}
      `;

      drawer.querySelector(".mobile-nav-close")?.addEventListener("click", closeDrawer);
      drawer.querySelectorAll(".mobile-nav-link").forEach((el) => {
        el.addEventListener("click", closeDrawer);
      });
      drawer.querySelector("#mobile-nav-logout")?.addEventListener("click", () => {
        if (typeof Auth !== "undefined") Auth.clear();
        window.location.href = "/login.html?logout=1";
      });
    };

    const openDrawer = () => {
      renderDrawer();
      drawer.classList.add("is-open");
      backdrop.classList.add("is-open");
      drawer.setAttribute("aria-hidden", "false");
      toggleBtn.setAttribute("aria-expanded", "true");
      document.body.classList.add("mobile-drawer-open");
    };

    const closeDrawer = () => {
      drawer.classList.remove("is-open");
      backdrop.classList.remove("is-open");
      drawer.setAttribute("aria-hidden", "true");
      toggleBtn.setAttribute("aria-expanded", "false");
      document.body.classList.remove("mobile-drawer-open");
    };

    toggleBtn.addEventListener("click", () => {
      if (drawer.classList.contains("is-open")) closeDrawer();
      else openDrawer();
    });
    backdrop.addEventListener("click", closeDrawer);
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && drawer.classList.contains("is-open")) closeDrawer();
    });
    window.addEventListener("resize", () => {
      if (window.innerWidth > 900 && drawer.classList.contains("is-open")) closeDrawer();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initMobileNav);
  } else {
    initMobileNav();
  }

  global.CareerHubUI = {
    toast: showToast,
    renderLoading,
    renderEmpty,
    renderError,
    escapeHtml,
  };
  global.showToast = showToast;
})(window);
