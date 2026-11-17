// main.js - Career Hub Dashboard Interactions

document.addEventListener('DOMContentLoaded', () => {
  // Elements for mobile drawer
  const hamburger = document.getElementById('hamburger');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('overlay');

  function openSidebar() {
    if (sidebar) sidebar.classList.add('open');
    if (overlay) overlay.classList.add('show');
    document.body.classList.add('drawer-open');
  }

  function closeSidebar() {
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('show');
    document.body.classList.remove('drawer-open');
  }

  if (hamburger) {
    hamburger.addEventListener('click', (e) => {
      e.stopPropagation();
      if (sidebar && sidebar.classList.contains('open')) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });
  }

  if (overlay) {
    overlay.addEventListener('click', closeSidebar);
  }

  // Close sidebar on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && sidebar && sidebar.classList.contains('open')) {
      closeSidebar();
    }
  });

  // Close sidebar when a navigation link is clicked (on mobile/tablet)
  const menuLinks = document.querySelectorAll('.sidebar-menu a');
  menuLinks.forEach((link) => {
    link.addEventListener('click', () => {
      if (window.innerWidth < 992) {
        closeSidebar();
      }
    });
  });

  // Tab switching interaction
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach((btn) => {
    btn.addEventListener('click', function () {
      tabBtns.forEach((b) => b.classList.remove('active'));
      this.classList.add('active');
    });
  });

  // Pagination number click interaction
  const pageNumbers = document.querySelectorAll('.page-number');
  pageNumbers.forEach((pageBtn) => {
    pageBtn.addEventListener('click', function () {
      pageNumbers.forEach((p) => p.classList.remove('active'));
      this.classList.add('active');
    });
  });
});
