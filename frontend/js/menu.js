document.addEventListener("DOMContentLoaded", function () {
    const sidebarContainer = document.getElementById("sidebar-container");
    if (!sidebarContainer) return;

    const menuItems = [

        { text: "Công số hàng ngày", icon: "fa-file-invoice", link: "/attendance-system/frontend/daily_reports.html" },
        { text: "Dashboard", icon: "fa-gauge", link: "dashboard.html" },
        { text: "Thời gian làm việc", icon: "fa-clock", link: "/attendance-system/frontend/pages/TimeTracking/TimeTracking.html" },
        { text: "Thông báo", icon: "fa-bell", link: "/attendance-system/frontend/pages/Notifications/notifications.html" },
        { text: "Thông tin nhân viên", icon: "fa-user", link: "/attendance-system/frontend/pages/Employees/employees.html" },
        { text: "Ngày nghỉ", icon: "fa-calendar-check", link: "/attendance-system/frontend/pages/TimeOff/timeoff.html" },
        { text: "Cài Đặt", icon: "fa-gear", link: "/attendance-system/frontend/pages/Setting/Setting_System.html" },
    ];

    // Lấy tên file hiện tại từ URL (ví dụ: daily_reports.html)
    // const currentPath = window.location.pathname.split("/").pop() || "index.html";

    let menuHtml = `
    <div class="logo d-flex align-items-center gap-2 p-3" style="color: white; font-weight: bold; font-size: 18px">
      <div class="d-flex align-items-center justify-content-center rounded-circle" style="width: 35px; height: 35px; background-color: #ff9800">
        <i class="fa-solid fa-play" style="color: white; font-size: 12px"></i>
      </div>
      Hệ thống tính công
    </div>
    <ul id="main-menu" style="list-style: none; padding: 0; margin-top: 10px; color: #ced4da">
  `;

    // menuItems.forEach((item) => {
    //     // Chuẩn hóa link để so sánh: xóa bỏ "./" nếu có
    //     const isActive = window.location.pathname.includes(item.link)
    //         ? "active-menu"
    //         : "";

    //     menuHtml += `
    //   <li class="${isActive}">
    //     <a href="${item.link}" style="text-decoration: none; color: inherit; display: block; padding: 12px 20px;">
    //       <i class="fa-solid ${item.icon}" style="width: 25px"></i> ${item.text}
    //     </a>
    //   </li>
    // `;
    // });

    menuHtml += `</ul>`;
    sidebarContainer.innerHTML = menuHtml;
});