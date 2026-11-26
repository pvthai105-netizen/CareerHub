document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("[data-chat-form]");
  const input = document.querySelector("[data-chat-input]");
  const transcript = document.querySelector("[data-chat-transcript]");
  const welcome = document.querySelector(".chat-welcome");
  const loading = document.querySelector("[data-chat-loading]");
  const sendButton = form?.querySelector('button[type="submit"]');
  const promptButtons = document.querySelectorAll("[data-chat-prompt]");

  if (!form || !input || !transcript || !loading || !sendButton) return;

  const apiOrigin = `${window.location.protocol}//${window.location.hostname}:8000`;
  const chatUrl = `${apiOrigin}/api/chat`;
  const scrollToEnd = () => transcript.scrollTo({
    top: transcript.scrollHeight,
    behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth",
  });

  const escapeHTML = (value) => String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");

  const formatInlineMarkdown = (value) => escapeHTML(value)
    .replace(/\\\*/g, "*")
    .replace(/\\_/g, "_")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/__(.+?)__/g, "<strong>$1</strong>")
    .replace(/(^|[^*])\*([^*\n]+)\*(?!\*)/g, "$1<em>$2</em>")
    .replace(/(^|[^_])_([^_\n]+)_(?!_)/g, "$1<em>$2</em>")
    .replace(/&lt;br\s*\/?&gt;/gi, "<br>");

  const renderMarkdown = (value) => {
    const lines = String(value ?? "").replace(/\r/g, "").split("\n");
    const blocks = [];
    let paragraph = [];
    let listType = "";
    let listItems = [];

    const flushParagraph = () => {
      if (!paragraph.length) return;
      blocks.push(`<p>${paragraph.map(formatInlineMarkdown).join("<br>")}</p>`);
      paragraph = [];
    };
    const flushList = () => {
      if (!listItems.length) return;
      const tag = listType === "ordered" ? "ol" : "ul";
      blocks.push(`<${tag}>${listItems.map((item) => `<li>${formatInlineMarkdown(item)}</li>`).join("")}</${tag}>`);
      listItems = [];
      listType = "";
    };

    const parseTableRow = (line) => {
      const normalized = line.trim().replace(/\\\|/g, "|").replace(/\\\s*$/, "");
      if (!normalized.includes("|")) return null;
      const cells = normalized.split("|");
      if (cells[0].trim() === "") cells.shift();
      if (cells[cells.length - 1]?.trim() === "") cells.pop();
      return cells.length > 1 ? cells.map((cell) => cell.trim()) : null;
    };

    const isTableDivider = (cells) =>
      cells?.every((cell) => /^:?-{3,}:?$/.test(cell.replace(/\s/g, "")));

    const formatTableCell = (cell) => formatInlineMarkdown(cell)
      .replace(/(<br>\s*)?•\s*/g, (match) => match.startsWith("<br>") ? "<br>• " : "• ");

    for (let index = 0; index < lines.length; index += 1) {
      const line = lines[index];
      const tableHeader = parseTableRow(line);
      const tableDivider = parseTableRow(lines[index + 1] || "");
      if (tableHeader && isTableDivider(tableDivider) && tableHeader.length === tableDivider.length) {
        flushParagraph();
        flushList();
        const rows = [];
        index += 2;
        while (index < lines.length) {
          const row = parseTableRow(lines[index]);
          if (!row) break;
          rows.push(row);
          index += 1;
        }
        index -= 1;
        const headerHTML = tableHeader.map((cell) => `<th scope="col">${formatTableCell(cell)}</th>`).join("");
        const rowsHTML = rows.map((row) => `<tr>${tableHeader.map((_, cellIndex) =>
          `<td>${formatTableCell(row[cellIndex] || "")}</td>`).join("")}</tr>`).join("");
        blocks.push(`<div class="chat-table-wrap" role="region" aria-label="Bảng trong câu trả lời" tabindex="0"><table><thead><tr>${headerHTML}</tr></thead><tbody>${rowsHTML}</tbody></table></div>`);
        continue;
      }

      const unordered = line.match(/^\s*\\?[*+-]\s+(.+)$/);
      const ordered = line.match(/^\s*\d+[.)]\s+(.+)$/);
      const nextListType = unordered ? "unordered" : ordered ? "ordered" : "";
      if (nextListType) {
        flushParagraph();
        if (listType && listType !== nextListType) flushList();
        listType = nextListType;
        listItems.push(unordered ? unordered[1] : ordered[1]);
        continue;
      }

      flushList();
      const heading = line.match(/^\s{0,3}(#{1,3})\s+(.+)$/);
      if (heading) {
        flushParagraph();
        const level = heading[1].length;
        blocks.push(`<h${level}>${formatInlineMarkdown(heading[2])}</h${level}>`);
      } else if (line.trim()) {
        paragraph.push(line);
      } else {
        flushParagraph();
      }
    }

    flushList();
    flushParagraph();
    return blocks.join("");
  };

  const addMessage = (sender, message, createdAt) => {
    const isUser = sender === "user";
    const article = document.createElement("article");
    article.className = `chat-message chat-message--${isUser ? "user" : "assistant"}`;

    const avatar = document.createElement("div");
    avatar.className = "chat-message-avatar";
    avatar.setAttribute("aria-hidden", "true");
    if (isUser) {
      avatar.textContent = "BẠN";
    } else {
      const icon = document.createElement("span");
      icon.className = "material-symbols-outlined";
      icon.textContent = "smart_toy";
      avatar.append(icon);
    }

    const content = document.createElement("div");
    content.className = "chat-message-content";
    const meta = document.createElement("div");
    meta.className = "chat-message-meta";
    const author = document.createElement("span");
    author.className = "chat-message-author";
    author.textContent = isUser ? "Bạn" : "CareerHub AI";
    const time = document.createElement("time");
    const date = createdAt ? new Date(createdAt) : new Date();
    if (!Number.isNaN(date.getTime())) {
      time.dateTime = date.toISOString();
      time.textContent = new Intl.DateTimeFormat("vi-VN", { hour: "2-digit", minute: "2-digit" }).format(date);
    }
    meta.append(...(isUser ? [time, author] : [author, time]));

    const bubble = document.createElement("div");
    bubble.className = "chat-bubble";
    bubble.innerHTML = renderMarkdown(message);
    content.append(meta, bubble);
    article.append(avatar, content);
    transcript.insertBefore(article, loading);
    return article;
  };

  const showError = (message) => addMessage("assistant", message || "Không thể kết nối trợ lý AI. Vui lòng thử lại.");

  const parseResponse = async (response) => {
    let data;
    try {
      data = await response.json();
    } catch {
      throw new Error("Máy chủ trả về dữ liệu không hợp lệ.");
    }
    if (!response.ok) {
      const detail = data?.detail;
      const message = Array.isArray(detail)
        ? detail.map((item) => item.msg).filter(Boolean).join(" ")
        : detail || data?.message;
      throw new Error(message || `Yêu cầu thất bại (HTTP ${response.status}).`);
    }
    return data;
  };

  const getHeaders = (json = false) => {
    const headers = {};
    const token = localStorage.getItem("careerhub_token");
    if (token) headers.Authorization = `Bearer ${token}`;
    if (json) headers["Content-Type"] = "application/json";
    return headers;
  };

  const loadHistory = async () => {
    if (!localStorage.getItem("careerhub_token")) {
      welcome?.remove();
      showError("Vui lòng đăng nhập bằng tài khoản sinh viên để sử dụng trợ lý và xem lịch sử chat.");
      return;
    }
    try {
      const response = await fetch(`${chatUrl}/history`, { headers: getHeaders() });
      const history = await parseResponse(response);
      if (history.length) {
        welcome?.remove();
        history.forEach((item) => addMessage(item.sender, item.message, item.created_at));
        scrollToEnd();
      }
    } catch (error) {
      welcome?.remove();
      showError(error.message);
    }
  };

  promptButtons.forEach((button) => button.addEventListener("click", () => {
    input.value = button.dataset.chatPrompt || "";
    input.focus();
  }));

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const message = input.value.trim();
    if (!message || sendButton.disabled) return;

    welcome?.remove();
    addMessage("user", message);
    input.value = "";
    loading.hidden = false;
    loading.classList.add("is-visible");
    sendButton.disabled = true;
    form.setAttribute("aria-busy", "true");
    scrollToEnd();

    try {
      const response = await fetch(chatUrl, {
        method: "POST",
        headers: getHeaders(true),
        body: JSON.stringify({ message }),
      });
      const data = await parseResponse(response);
      addMessage("assistant", data.reply);
    } catch (error) {
      showError(error.message);
    } finally {
      loading.hidden = true;
      loading.classList.remove("is-visible");
      sendButton.disabled = false;
      form.removeAttribute("aria-busy");
      input.focus();
      scrollToEnd();
    }
  });

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      form.requestSubmit();
    }
  });

  loadHistory();
});
