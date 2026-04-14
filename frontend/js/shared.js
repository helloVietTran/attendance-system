// Inject component app header 
$(document).ready(function () {
  initHeader();
});

async function checkAuthAndGetUser() {
    const token = localStorage.getItem("access_token");

    if (!token) {
        redirectToLogin();
        return;
    }

    try {
        const res = await fetchWithAuth(API_URL + "/employees/me");

        if (!res.ok) {
            // Nếu token không hợp lệ (401) hoặc lỗi server
            throw new Error("Unauthorized or Session Expired");
        }

        const result = await res.json();

        localStorage.setItem("user", JSON.stringify(result.data));
        updateHeaderUserInfo();
    } catch (err) {
        console.error("Auth Error:", err);

        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        redirectToLogin();
    }
}

function redirectToLogin() {
    window.location.href = "./login.html";
}

async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem("access_token");
    return await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
            "Authorization": `Bearer ${token}`
        }
    });
}

function logout() {
    localStorage.removeItem("user");
    localStorage.removeItem("access_token");
    redirectToLogin();
}

// lấy user từ localstorage tiêm vào header
function updateHeaderUserInfo() {
    const userStr = localStorage.getItem("user");
    if (userStr) {
        const user = JSON.parse(userStr);

        $('#user-email-display').text(user.email || 'N/A');

        const displayChar = user.full_name ? user.full_name.charAt(0) : (user.email ? user.email.charAt(0) : 'U');
        $('#user-name-badge').text(displayChar.toUpperCase());
    }
}

function showToast(message, type = 'success') {
    const $toastEl = $('#liveToast');

    $toastEl.removeClass('bg-success bg-danger');
    $toastEl.addClass(type === 'success' ? 'bg-success' : 'bg-danger');

    $('#toast-message').text(message);

    const toast = new bootstrap.Toast($toastEl[0]);
    toast.show();
}


// HEADER

function renderHeader() {
    return `
    <header id="header-container" class="app-header">
      <div class="header-inner">
        <div class="search-bar"></div>

        <div class="d-flex gap-4 align-items-center">
          
          <!-- Notification -->
          <div class="notification-wrapper">
            <button class="notification-btn" id="noti-btn">
              <i class="fa-regular fa-bell"></i>
              <span id="noti-badge" class="noti-badge d-none">0</span>
            </button>

            <div id="notification-dropdown" class="notification-dropdown d-none">
              <div class="noti-header">
                <span>Thông báo</span>
              </div>
              <div id="notification-list" class="noti-list">
                <div class="noti-empty">Đang tải...</div>
              </div>
            </div>
          </div>

          <!-- User -->
          <div class="user-profile d-flex align-items-center gap-3">
            <div id="user-name-badge" class="user-badge">U</div>
            <span id="user-email-display" class="user-email">---</span>

            <button onclick="logout()" class="btn btn-link btn-logout">
              <i class="fa-solid fa-right-from-bracket"></i> Đăng xuất
            </button>
          </div>
        </div>
      </div>
    </header>
  `;
}

function bindHeaderEvents() {
    const btn = document.getElementById("noti-btn");
    const dropdown = document.getElementById("notification-dropdown");

    if (!btn) return;

    btn.addEventListener("click", function (e) {
        e.stopPropagation();
        dropdown.classList.toggle("d-none");

        if (!dropdown.classList.contains("d-none")) {
            loadNotifications();
        }
    });

    // click outside
    document.addEventListener("click", function (e) {
        if (!e.target.closest(".notification-wrapper")) {
            dropdown.classList.add("d-none");
        }
    });
}

function initHeader(containerId = "header-container") {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = renderHeader();

    bindHeaderEvents();
}

function bindHeaderEvents() {
    const btn = document.getElementById("noti-btn");
    const dropdown = document.getElementById("notification-dropdown");

    if (!btn) return;

    btn.addEventListener("click", function (e) {
        e.stopPropagation();
        dropdown.classList.toggle("d-none");

        if (!dropdown.classList.contains("d-none")) {
            loadNotifications();
        }
    });

    // click outside
    document.addEventListener("click", function (e) {
        if (!e.target.closest(".notification-wrapper")) {
            dropdown.classList.add("d-none");
        }
    });
}

function loadNotifications() {
    const now = new Date();

    $.ajax({
        url: `/notifications/me`,
        method: "GET",
        data: {
            month: now.getMonth() + 1,
            year: now.getFullYear()
        },
        success: function (res) {
            renderNotifications(res.data);
        },
        error: function (err) {
            console.error(err);
        }
    });
}


function renderNotifications(list) {
    const container = document.getElementById("notification-list");

    if (!list.length) {
        container.innerHTML = `<div class="noti-empty">Không có thông báo</div>`;
        return;
    }

    let unreadCount = 0;

    container.innerHTML = list.map(noti => {
        if (!noti.is_read) unreadCount++;

        return `
      <div class="noti-item ${!noti.is_read ? "unread" : ""}" onclick="markAsRead(${noti.id})">
        <div class="noti-title">${noti.title}</div>
        <div class="noti-content">${noti.content}</div>
        <div class="noti-time">${formatTime(noti.created_at)}</div>
      </div>
    `;
    }).join("");

    // badge
    const badge = document.getElementById("noti-badge");
    if (unreadCount > 0) {
        badge.classList.remove("d-none");
        badge.innerText = unreadCount;
    } else {
        badge.classList.add("d-none");
    }
}

function toggleNotification() {
    const dropdown = document.getElementById("notification-dropdown");
    dropdown.classList.toggle("d-none");

    if (!dropdown.classList.contains("d-none")) {
        loadNotifications();
    }
}

function markAsRead(id) {
    $.ajax({
        url: `/notifications/mark-read?ids=${id}`,
        method: "PATCH",
        success: function () {
            loadNotifications();
        },
        error: function (err) {
            console.error(err);
        }
    });
}
function formatTime(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleString("vi-VN");
}