document.addEventListener("DOMContentLoaded", function () {
  const sidebarContainer = document.getElementById("sidebar-container");
  if (!sidebarContainer) return;

  const menuItems = [
    { text: "Công số hàng ngày", icon: "fa-file-invoice", link: "daily_reports.html" },
    { text: "Chấm công", icon: "fa-id-badge", link: "attendance.html" },
    { text: "Dashboard", icon: "fa-gauge", link: "dashboard.html" },
    { text: "Thời gian làm việc", icon: "fa-clock", link: "working_time.html" },
    { text: "Thông báo", icon: "fa-bell", link: "notifications.html" },
    { text: "Thông tin nhân viên", icon: "fa-user", link: "profile.html" },
    { text: "Ngày nghỉ", icon: "fa-calendar-check", link: "leave_requests.html" },
    { text: "Cài Đặt", icon: "fa-gear", link: "settings.html" },
  ];

  // Lấy tên file hiện tại từ URL (ví dụ: daily_reports.html)
  const currentPath = window.location.pathname.split("/").pop() || "index.html";

  let menuHtml = `
    <div class="logo d-flex align-items-center gap-2 p-3" style="color: white; font-weight: bold; font-size: 18px">
      <div class="d-flex align-items-center justify-content-center rounded-circle" style="width: 35px; height: 35px; background-color: #ff9800">
        <i class="fa-solid fa-play" style="color: white; font-size: 12px"></i>
      </div>
      Hệ thống tính công
    </div>
    <ul id="main-menu" style="list-style: none; padding: 0; margin-top: 10px; color: #ced4da">
  `;

  menuItems.forEach((item) => {
    // Chuẩn hóa link để so sánh: xóa bỏ "./" nếu có
    const normalizedLink = item.link.replace("./", "");
    const isActive = currentPath === normalizedLink ? "active-menu" : "";
    
    menuHtml += `
      <li class="${isActive}">
        <a href="${item.link}" style="text-decoration: none; color: inherit; display: block; padding: 12px 20px;">
          <i class="fa-solid ${item.icon}" style="width: 25px"></i> ${item.text}
        </a>
      </li>
    `;
  });

  menuHtml += `</ul>`;
  sidebarContainer.innerHTML = menuHtml;
});