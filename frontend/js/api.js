// Tự động nhận diện: Nếu chạy Live Server (port 5500) thì trỏ port 8000, 
// nếu chạy qua FastAPI hoặc đã deploy lên Render thì dùng domain hiện tại ("")
const API_BASE = window.location.port === "5500" ? "http://127.0.0.1:8000" : "";// Thêm tiền tố API chung để đồng nhất các endpoint backend
const API_PREFIX = "/api"; // ← đã thêm cơ chế xử lý tiền tố API

/**
 * Xây dựng URL hoàn chỉnh cho các request.
 * Nếu path bắt đầu bằng "/user" (đường dẫn đã có tiền tố riêng), không thêm API_PREFIX.
 * Ngược lại, tự động chèn "/api" để trùng khớp với các router FastAPI.
 */

function buildUrl(path) {
  // Đảm bảo đường dẫn luôn bắt đầu bằng dấu /
  const cleanPath = path.startsWith("/") ? path : "/" + path;

  // Nếu đường dẫn đã có /api hoặc /user thì giữ nguyên
  if (
    cleanPath.startsWith("/api/") ||
    cleanPath === "/api" ||
    cleanPath.startsWith("/user/") ||
    cleanPath === "/user"
  ) {
    return cleanPath;
  }

  // Nếu chưa có tiền tố thì tự thêm /api
  return API_PREFIX + cleanPath;
}


const TOKEN_KEY = "careerhub_token";

const Auth = {
  getToken: () => localStorage.getItem(TOKEN_KEY),
  setToken: (token) => localStorage.setItem(TOKEN_KEY, token),
  clear: () => localStorage.removeItem(TOKEN_KEY),
};

async function apiFetch(path, options = {}) {
  const headers = { ...(options.headers || {}) };
  const token = Auth.getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let body = options.body;
  if (body && !(body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(body);
  }

  let response;
  try {
    response = await fetch(API_BASE + buildUrl(path), { ...options, headers, body });
  } catch (netErr) {
    throw new Error("Không thể kết nối đến máy chủ Backend (hãy kiểm tra xem uvicorn đã chạy chưa)");
  }

  if (response.status === 401) {
    Auth.clear();
    // Nếu đang không ở trang login hay register thì tự chuyển về login
    // if (!window.location.pathname.includes("login.html") && !window.location.pathname.includes("register.html")) {
    //   window.location.href = "/login.html?expired=1";
    // }
  }

  let data = null;
  let text = "";
  try {
    text = await response.text();
    data = JSON.parse(text);
  } catch (e) {
    // Phản hồi không phải JSON (có thể là lỗi 500 hoặc trang 404 HTML)
  }

  if (!response.ok) {
    let errorMsg = "Có lỗi xảy ra";
    const apiError = data?.detail ?? data?.message;
    if (apiError) {
      if (typeof apiError === "string") {
        errorMsg = apiError;
      } else if (Array.isArray(apiError) && apiError.length > 0) {
        errorMsg = apiError[0].msg || JSON.stringify(apiError);
      } else {
        errorMsg = JSON.stringify(apiError);
      }
    } else if (text) {
      errorMsg = text.length < 100 ? text : `Lỗi máy chủ (${response.status})`;
    }
    throw new Error(errorMsg);
  }

  return data;
}

const api = {
  get: (path) => apiFetch(path),
  post: (path, body) => apiFetch(path, { method: "POST", body }),
  put: (path, body) => apiFetch(path, { method: "PUT", body }),
  patch: (path, body) => apiFetch(path, { method: "PATCH", body }),
  delete: (path) => apiFetch(path, { method: "DELETE" }),
};

// Ý chính của từng phần:

// Auth: lưu, đọc, xoá token trong trình duyệt (localStorage).
// apiFetch: nếu có token thì thêm header Authorization: Bearer <token>, nếu gửi dữ liệu thì tự chuyển thành JSON, nếu server báo lỗi thì ném ra thông báo dễ đọc.
// api.get/post/put/delete: cách gọi ngắn gọn, ví dụ api.get("/health") sẽ gọi /api/health.
