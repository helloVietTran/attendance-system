/**
 * reports-main.js
 * Khởi tạo trang Reports chính
 */

async function initReportsMainPage() {
    console.log("Kích hoạt trang Reports chính...");

    const reportsNav = document.querySelector('.reports-nav');
    if (!reportsNav) {
        console.error('Không tìm thấy reports-nav');
        return;
    }

    // Mặc định load trang Chấm Công vào bên phải ngay khi mở
    await loadReportPage('attendance');

    // Sử dụng Event Delegation để xử lý click menu
    reportsNav.addEventListener('click', async (e) => {
        const navItem = e.target.closest('.reports-nav-item');
        if (!navItem) return;

        // Xóa class active ở các mục khác
        document.querySelectorAll('.reports-nav-item').forEach(el => el.classList.remove('active'));
        // Thêm class active vào mục vừa chọn
        navItem.classList.add('active');

        // Lấy key trang cần load
        const pageKey = navItem.getAttribute('data-report-page');
        console.log('Loading report page:', pageKey);
        await loadReportPage(pageKey);
    });
}

/**
 * Load các form báo cáo chi tiết vào panel bên phải
 */
async function loadReportPage(pageKey) {
    let filePath = '';
    const cssFile = '../../pages/Reports/reports.css';

    // Bản đồ đường dẫn file dựa trên key
    const routes = {
        'attendance': '../../pages/Reports/attendance.html',
        'daily_reports': '../../pages/Reports/reports.html'
    };

    filePath = routes[pageKey];

    if (filePath) {
        try {
            const success = await loadComponent('reports-content-panel', filePath, cssFile);
            if (success) {
                console.log('Page loaded:', pageKey);
                // Chờ một chút để DOM được cập nhật
                setTimeout(() => {
                    if (pageKey === 'attendance') {
                        if (typeof initAttendancePage === 'function') {
                            console.log('Calling initAttendancePage');
                            initAttendancePage();
                        } else {
                            console.error('initAttendancePage function not found');
                        }
                    } else if (pageKey === 'daily_reports') {
                        if (typeof initReportsPage === 'function') {
                            console.log('Calling initReportsPage');
                            initReportsPage();
                        } else {
                            console.error('initReportsPage function not found');
                        }
                    }
                }, 100);
            }
        } catch (error) {
            console.error('Error loading report page:', error);
            document.getElementById('reports-content-panel').innerHTML =
                `<div style="padding:40px; text-align: center; color:#f44336;">Lỗi khi tải trang: ${error.message}</div>`;
        }
    } else {
        document.getElementById('reports-content-panel').innerHTML =
            `<div style="padding:40px; text-align: center; color:#888;">Trang "${pageKey}" không tồn tại.</div>`;
    }
}
