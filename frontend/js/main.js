document.getElementById("btn-health").addEventListener("click", async () => {
  const result = document.getElementById("health-result");
  try {
    const data = await api.get("/health");
    result.textContent = "Backend trả về: " + data.status;
  } catch (error) {
    result.textContent = "Lỗi: " + error.message;
  }
});