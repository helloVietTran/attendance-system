document.addEventListener("DOMContentLoaded", function () {
  const sidebarContainer = document.getElementById("sidebar-container");
  if (!sidebarContainer) return;

  const menuItems = [
    { text: "Công số hàng ngày", icon: "fa-file-invoice", link: "daily_reports.html" },
    { text: "Chấm công", icon: "fa-id-badge", link: "attendance.html" },
    { text: "Lịch làm việc", icon: "fa-calendar-check", link: "calendar.html" },
    { text: "Thông báo", icon: "fa-bell", link: "notifications.html" },
    { text: "Cài Đặt", icon: "fa-gear", link: "setting_system.html" },
  ];

  const currentPath = window.location.pathname.split("/").pop() || "index.html";

  let menuHtml = `
    <!-- Header sidebar -->
    <div class="d-flex justify-content-between align-items-center p-3" style="color:white;">
        <div class="d-flex align-items-center gap-2">
            <div style="width:35px;height:35px;background:#ff9800;border-radius:50%;display:flex;align-items:center;justify-content:center;">
                <i class="fa-solid fa-play" style="font-size:12px;color:white;"></i>
            </div>
            <span style="font-weight:bold;">Hệ thống</span>
        </div>

        <!-- Close button (mobile) -->
        <button id="close-sidebar" class="btn text-white d-md-none">
            <i class="fa-solid fa-xmark"></i>
        </button>
    </div>

    <ul style="list-style:none;padding:0;color:#ced4da;">
  `;

  menuItems.forEach((item) => {
    const normalizedLink = item.link.replace("./", "");
    const isActive = currentPath === normalizedLink ? "active-menu" : "";

    menuHtml += `
      <li class="${isActive}">
        <a href="${item.link}" style="display:block;padding:12px 20px;color:inherit;text-decoration:none;">
          <i class="fa-solid ${item.icon}" style="width:25px;"></i> ${item.text}
        </a>
      </li>
    `;
  });

  menuHtml += `</ul>`;
  sidebarContainer.innerHTML = menuHtml;

  // ===== TOGGLE =====
  const toggleBtn = document.getElementById("menu-toggle");
  const closeBtn = document.getElementById("close-sidebar");
  const overlay = document.getElementById("sidebar-overlay");

  function openSidebar() {
    sidebarContainer.classList.add("active");
    overlay.classList.add("active");
    toggleBtn.classList.add("hide");
  }

  function closeSidebar() {
    sidebarContainer.classList.remove("active");
    overlay.classList.remove("active");
    toggleBtn.classList.remove("hide");
  }

  toggleBtn?.addEventListener("click", openSidebar);
  closeBtn?.addEventListener("click", closeSidebar);
  overlay?.addEventListener("click", closeSidebar);
});