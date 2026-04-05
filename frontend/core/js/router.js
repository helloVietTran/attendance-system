async function loadComponent(elementId, filePath, cssPath = null) {
    const container = document.getElementById(elementId);
    if (!container) return false;

    if (cssPath) {
        if (!document.querySelector(`link[href="${cssPath}"]`)) {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = cssPath;
            document.head.appendChild(link);
        }
    }

    try {
        const response = await fetch(filePath);
        const html = await response.text();
        container.innerHTML = html;
        return true;
    } catch (error) {
        container.innerHTML = "Lỗi tải nội dung.";
        return false;
    }
}

async function initApp() {
    // 1. Load Sidebar & Header (Không cần CSS riêng vì đã có main.css)
    await loadComponent('sidebar-container', '../layout/sidebar.html');
    await loadComponent('header-container', '../layout/header.html');

    // 2. Load Setting kèm theo CSS của nó
    // Truyền thêm tham số thứ 3 là đường dẫn file CSS
    const pageLoaded = await loadComponent(
        'main-content',
        '../../pages/Setting/setting.html',
        '../../pages/Setting/setting.css'
    );

    if (pageLoaded) {
        // Đảm bảo logic của trang Setting được kích hoạt
        if (typeof initSettingsPage === 'function') {
            initSettingsPage();
        }
    }

    setupMainSidebarLinks();
}

function setupMainSidebarLinks() {
    const sidebar = document.getElementById('sidebar-container');
    if (!sidebar) return;

    sidebar.onclick = async (e) => {
        const link = e.target.closest('li');
        if (!link) return;

        const menuText = link.innerText.trim();

        if (menuText.includes("Dashboard")) {
            await loadComponent('main-content', '../../pages/Dashboard/index.html', '../../pages/Dashboard/dashboard.css');
        } else if (menuText.includes("Thống kê")) {
            const success = await loadComponent('main-content', '../../pages/Reports/index.html', '../../pages/Reports/reports.css');
            if (success && typeof window.initReportsMainPageGlobal === 'function') {
                setTimeout(() => {
                    window.initReportsMainPageGlobal();
                }, 100);
            }
        } else if (menuText.includes("Cài Đặt")) {
            const success = await loadComponent('main-content', '../../pages/Setting/setting.html', '../../pages/Setting/setting.css');
            if (success && typeof initSettingsPage === 'function') {
                initSettingsPage();
            }
        }
    };
}



document.addEventListener('DOMContentLoaded', initApp);