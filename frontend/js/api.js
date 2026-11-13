const API_BASE = "/api";
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

  const response = await fetch(API_BASE + path, { ...options, headers, body });

  if (response.status === 401) {
    Auth.clear();
    // Nếu đang không ở trang login hay register thì tự chuyển về login
    if (!window.location.pathname.includes("login.html") && !window.location.pathname.includes("register.html")) {
      window.location.href = "/login.html?expired=1";
    }
  }
  
  let data = null;
  try {
    data = await response.json();
  } catch (e) {
    // phản hồi không có nội dung JSON
  }

  if (!response.ok) {
    throw new Error((data && data.detail) || "Có lỗi xảy ra");
  }
  return data;
}

const api = {
  get: (path) => apiFetch(path),
  post: (path, body) => apiFetch(path, { method: "POST", body }),
  put: (path, body) => apiFetch(path, { method: "PUT", body }),
  delete: (path) => apiFetch(path, { method: "DELETE" }),
};

// Ý chính của từng phần:

// Auth: lưu, đọc, xoá token trong trình duyệt (localStorage).
// apiFetch: nếu có token thì thêm header Authorization: Bearer <token>, nếu gửi dữ liệu thì tự chuyển thành JSON, nếu server báo lỗi thì ném ra thông báo dễ đọc.
// api.get/post/put/delete: cách gọi ngắn gọn, ví dụ api.get("/health") sẽ gọi /api/health.