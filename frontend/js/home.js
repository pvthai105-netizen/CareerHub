/**
 * home.js - Xử lý tương tác trên Trang chủ (home.html)
 * Yêu cầu:
 * - Khi chưa đăng nhập: Header hiển thị Đăng nhập / Đăng ký.
 * - Bất kỳ thao tác click vào chức năng nào (Menu, Tìm kiếm, Xem việc làm, Ngành nghề, Đăng tuyển...) đều chuyển hướng sang trang login.html.
 * - Khi đã đăng nhập: Cho phép thao tác bình thường, chuyển thẳng vào trang Hồ sơ cá nhân (profile.html).
 */
document.addEventListener("DOMContentLoaded", () => {
  // 1. Kiểm tra trạng thái đăng nhập từ AuthGuard
  const currentUser = typeof AuthGuard !== "undefined" ? AuthGuard.getUser() : null;

  // 2. Nếu người dùng CHƯA đăng nhập
  if (!currentUser) {
    // Các thành phần tương tác cần chuyển hướng sang login
    const interactiveSelectors = [
      ".nav-menu a:not([href='home.html'])", // Menu Tìm việc, Công ty, Trợ lý AI, Hồ sơ
      ".hero-search-box input",
      ".hero-search-box select",
      ".btn-hero-search",
      ".future-link",
      ".category-card",
      ".home-job-card",
      ".section-link",
      ".btn-employer-cta"
    ];

    const elementsToGate = document.querySelectorAll(interactiveSelectors.join(", "));

    elementsToGate.forEach((el) => {
      el.style.cursor = "pointer";

      el.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        window.location.href = "login.html";
      });
    });

    // Nếu gõ Enter trong ô tìm kiếm
    const searchInput = document.querySelector(".hero-search-box input");
    if (searchInput) {
      searchInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          window.location.href = "login.html";
        }
      });
    }
  }
});
