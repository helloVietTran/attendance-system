/**
 * Hàm khởi tạo các sự kiện cho trang Setting
 * Được gọi từ router.js sau khi setting.html đã được chèn vào DOM
 */
async function initSettingsPage() {
    console.log("Kích hoạt logic trang Settings...");

    const settingsNav = document.querySelector('.settings-nav');
    if (!settingsNav) return;

    // 1. Mặc định load trang System Config vào bên phải ngay khi mở
    await loadInternalSettingPage('system_config');

    // 2. Sử dụng Event Delegation để xử lý click menu con bên trái
    settingsNav.addEventListener('click', async (e) => {
        const navItem = e.target.closest('.settings-nav-item');
        if (!navItem) return;

        // Xóa class active ở các mục khác
        document.querySelectorAll('.settings-nav-item').forEach(el => el.classList.remove('active'));
        // Thêm class active vào mục vừa chọn
        navItem.classList.add('active');

        // Lấy key trang cần load
        const pageKey = navItem.getAttribute('data-page');
        await loadInternalSettingPage(pageKey);
    });
}

/**
 * Hàm load các form cài đặt chi tiết vào panel bên phải
 */
async function loadInternalSettingPage(pageKey) {
    let filePath = '';

    // Bản đồ đường dẫn file dựa trên key
    const routes = {
        'system_config': '../../pages/Setting/setting_system.html',
        'time_tracking': '../../pages/Setting/setting_time_tracking.html'
    };

    filePath = routes[pageKey];

    if (filePath) {
        const success = await loadComponent('settings-content-panel', filePath);
        if (success && pageKey === 'system_config') {
            setupSystemFormLogic();
        }
    } else {
        document.getElementById('settings-content-panel').innerHTML =
            `<div style="padding:20px; color:#888;">Giao diện cho "${pageKey}" đang được phát triển...</div>`;
    }
}

/**
 * Xử lý sự kiện Submit Form và thu thập dữ liệu theo KEY yêu cầu
 */
function setupSystemFormLogic() {
    const form = document.getElementById('system-settings-form');
    if (!form) return;

    form.onsubmit = function (e) {
        e.preventDefault(); // Ngăn trang web bị load lại

        // Lấy dữ liệu từ Form
        const formData = new FormData(form);
        const configData = {
            lunch_break_start: formData.get('lunch_break_start'),
            lunch_break_end: formData.get('lunch_break_end'),
            annual_paid_leave_days: parseInt(formData.get('annual_paid_leave_days')),
            maternity_leave_months: parseInt(formData.get('maternity_leave_months')),
            max_attendance_correction_per_month: parseInt(formData.get('max_attendance_correction_per_month'))
        };

        // Output kết quả
        console.log("%c [HỆ THỐNG] Dữ liệu cấu hình mới:", "color: #4caf50; font-weight: bold;", configData);

        alert("Lưu thành công!\nGiờ nghỉ: " + configData.lunch_break_start + " - " + configData.lunch_break_end);
    };
}