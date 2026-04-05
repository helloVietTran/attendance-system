/**
 * Hàm khởi tạo các sự kiện cho trang Setting
 * Được gọi từ router.js sau khi setting.html đã được chèn vào DOM
 */
const API_BASE_URL = "http://localhost:8000/api/v1";
const API_URL = API_BASE_URL + "/settings/";

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
async function setupSystemFormLogic() {
    const form = document.getElementById('system-settings-form');
    if (!form) return;

    await loadSystemSettings();

    form.onsubmit = async function (e) {
        e.preventDefault();

        console.log("🚀 Submit triggered");

        // 🔥 Lấy value an toàn (tránh NaN)
        const lunchStart = document.getElementById('lunch_break_start').value;
        const lunchEnd = document.getElementById('lunch_break_end').value;

        const annualLeave = parseInt(document.getElementById('annual_paid_leave_days').value) || 0;
        const maternity = parseInt(document.getElementById('maternity_leave_months').value) || 0;
        const maxAttendance = parseInt(document.getElementById('max_attendance_correction_per_month').value) || 0;

        // 🔥 Validate basic
        if (!lunchStart || !lunchEnd) {
            showNotification("❌ Vui lòng nhập giờ nghỉ trưa", "error");
            return;
        }

        const configs = [
            { key: "lunch_break_start", value: lunchStart },
            { key: "lunch_break_end", value: lunchEnd },
            { key: "annual_paid_leave_days", value: annualLeave },
            { key: "maternity_leave_months", value: maternity },
            { key: "max_attendance_correction_per_month", value: maxAttendance }
        ];

        console.log("📤 DATA GỬI:", configs);

        try {
            const token = localStorage.getItem("token");
            if (!token) {
                showNotification("❌ Vui lòng đăng nhập trước", "error");
                return;
            }

            const res = await fetch(API_URL, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify(configs)
            });

            const data = await res.json();

            console.log("📥 RESPONSE:", data);

            if (!res.ok) {
                throw new Error(data.detail || JSON.stringify(data));
            }

            showNotification("✅ Lưu thành công!", "success");

        } catch (err) {
            console.error("❌ ERROR:", err);
            showNotification("❌ Lỗi: " + err.message, "error");
        }
    };
}

/**
 * Hàm load dữ liệu settings từ API và điền vào form
 */
async function loadSystemSettings() {
    try {
        const token = localStorage.getItem("token");
        if (!token) {
            showNotification("❌ Vui lòng đăng nhập trước", "error");
            return;
        }

        const res = await fetch(API_URL, {
            method: "GET",
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        if (!res.ok) {
            throw new Error("Không thể tải dữ liệu settings");
        }

        const data = await res.json();
        console.log("📥 SETTINGS DATA:", data);

        // Giả sử data là array of {key, value, description}
        data.forEach(setting => {
            const element = document.getElementById(setting.key);
            if (element) {
                element.value = setting.value;
            }
        });

        showNotification("✅ Tải dữ liệu thành công", "success");

    } catch (err) {
        console.error("❌ ERROR loading settings:", err);
        showNotification("❌ Lỗi tải dữ liệu: " + err.message, "error");
    }
}

/**
 * Hàm hiển thị thông báo
 */
function showNotification(message, type = "info") {
    // Tạo element notification nếu chưa có
    let notification = document.getElementById('notification');
    if (!notification) {
        notification = document.createElement('div');
        notification.id = 'notification';
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 10px 20px;
            border-radius: 5px;
            color: white;
            font-weight: bold;
            z-index: 1000;
            display: none;
        `;
        document.body.appendChild(notification);
    }

    notification.textContent = message;
    notification.style.display = 'block';

    // Set color based on type
    if (type === "success") {
        notification.style.backgroundColor = "#4CAF50";
    } else if (type === "error") {
        notification.style.backgroundColor = "#f44336";
    } else {
        notification.style.backgroundColor = "#2196F3";
    }

    // Auto hide after 3 seconds
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}