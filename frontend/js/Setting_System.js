let originalSettings = {};
let currentSettings = {};

const settingLabels = {
    'lunch_break_start': 'Giờ bắt đầu giờ ăn trưa',
    'lunch_break_end': 'Giờ kết thúc giờ ăn trưa',
    'annual_paid_leave_days': 'Số ngày phép năm',
    'maternity_leave_months': 'Số tháng phép thai sản',
    'max_attendance_correction_per_month': 'Số lần sửa công/tháng'
};

const settingIcons = {
    'lunch_break_start': { icon: 'fa-clock', color: '#ff9800' },
    'lunch_break_end': { icon: 'fa-clock', color: '#ff5722' },
    'annual_paid_leave_days': { icon: 'fa-calendar-days', color: '#4caf50' },
    'maternity_leave_months': { icon: 'fa-person-pregnant', color: '#e91e63' },
    'max_attendance_correction_per_month': { icon: 'fa-pen-to-square', color: '#2196f3' }
};

const settingDescriptions = {
    'lunch_break_start': 'Thời gian bắt đầu giờ ăn trưa (định dạng HH:mm)',
    'lunch_break_end': 'Thời gian kết thúc giờ ăn trưa (định dạng HH:mm)',
    'annual_paid_leave_days': 'Tổng số ngày phép được hưởng mỗi năm',
    'maternity_leave_months': 'Số tháng phép thai sản cho lao động nữ',
    'max_attendance_correction_per_month': 'Số lần tối đa được phép chỉnh sửa công mỗi tháng'
};

document.addEventListener('DOMContentLoaded', async function () {
    await initSettingsPage();
});

async function initSettingsPage() {
    await checkAuthAndGetUser();
    const user = JSON.parse(localStorage.getItem("user"));
    if (!user) {
        showToast('Lỗi: Không tìm thấy thông tin người dùng', 'error');
        return;
    }
    await loadSettings();
    const saveBtn = document.getElementById('save-settings-btn');
    const resetBtn = document.getElementById('reset-settings-btn');
    if (saveBtn) saveBtn.addEventListener('click', saveSettings);
    if (resetBtn) resetBtn.addEventListener('click', resetSettings);
}

async function loadSettings() {
    const container = document.getElementById('settings-container');
    try {
        const response = await fetchWithAuth(`${API_URL}/settings`);
        if (!response.ok) throw new Error(`API Error: ${response.status}`);
        const result = await response.json();

        if (result.status === 1000 && result.data) {
            originalSettings = {};
            currentSettings = {};
            const settingsArray = Array.isArray(result.data) ? result.data : [result.data];
            settingsArray.forEach(setting => {
                if (setting && setting.key) {
                    originalSettings[setting.key] = setting.value;
                    currentSettings[setting.key] = setting.value;
                }
            });

            renderSettings(settingsArray);
        } else {
            throw new Error('Invalid API response format');
        }
    } catch (error) {

        container.innerHTML = `<div class="text-center" style="padding: 40px; color: red;"><i class="fa-solid fa-exclamation-triangle" style="font-size: 24px;"></i><p style="margin-top: 10px;">Lỗi: ${error.message}</p></div>`;
        showToast('Lỗi khi tải cài đặt: ' + error.message, 'error');
    }
}

function renderSettings(settingsArray) {
    const container = document.getElementById('settings-container');

    let html = `
        <div style="
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
        ">
    `;

    settingsArray.forEach(setting => {
        if (setting && setting.key) {
            const label = settingLabels[setting.key] || setting.key;
            const description = settingDescriptions[setting.key] || setting.description || '';
            const inputType = setting.key.includes('lunch') ? 'time' : 'number';
            const value = setting.value || '';
            const min = inputType === 'number' ? 'min="0"' : '';

            const iconData = settingIcons[setting.key] || {
                icon: 'fa-gear',
                color: '#007bff'
            };

            html += `
                <div style="
                    padding: 18px;
                    border-radius: 12px;
                    border: 1px solid #e0e0e0;
                    background: #ffffff10;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                    transition: all 0.2s ease;
                "
                onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 16px rgba(0,0,0,0.08)'"
                onmouseout="this.style.transform='none';this.style.boxShadow='0 4px 12px rgba(0,0,0,0.05)'"
                >
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                        <i class="fa-solid ${iconData.icon}" 
                           style="
                                color:${iconData.color};
                                font-size:16px;
                                width:30px;
                                height:30px;
                                display:flex;
                                align-items:center;
                                justify-content:center;
                                background:${iconData.color}20;
                                border-radius:6px;
                           ">
                        </i>

                        <label style="
                            font-size: 14px;
                            font-weight: 600;
                            color: #262626;
                            margin:0;
                        ">
                            ${label}
                        </label>
                    </div>

                    <p style="
                        font-size: 12px;
                        color: #888;
                        margin-bottom: 10px;
                        margin-left:40px;
                    ">
                        ${description}
                    </p>

                    <input 
                        type="${inputType}" 
                        id="input-${setting.key}" 
                        value="${value}" 
                        class="custom-input"
                        ${min}
                        style="width: 100%;"
                    />
                </div>
            `;
        }
    });

    html += `</div>`;
    container.innerHTML = html;
}

async function saveSettings() {
    const updates = [];
    for (const key in originalSettings) {
        const inputElement = document.getElementById(`input-${key}`);
        if (inputElement) {
            const newValue = inputElement.value;
            if (newValue !== originalSettings[key]) {
                updates.push({ key: key, value: newValue });
            }
        }
    }
    if (updates.length === 0) {
        showToast('Không có thay đổi để lưu', 'info');
        return;
    }

    const saveBtn = document.getElementById('save-settings-btn');
    const originalHTML = saveBtn.innerHTML;
    saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang lưu...';
    saveBtn.disabled = true;
    try {
        const response = await fetchWithAuth(`${API_URL}/settings`, { method: 'PUT', body: JSON.stringify(updates) });
        if (!response.ok) throw new Error(`API Error: ${response.status}`);
        const result = await response.json();

        if (result.status === 1000) {
            updates.forEach(update => { originalSettings[update.key] = update.value; });
            showToast('Cài đặt đã được lưu thành công', 'success');
        } else {
            throw new Error(result.detail || 'Lỗi không xác định');
        }
    } catch (error) {

        showToast('Lỗi khi lưu cài đặt: ' + error.message, 'error');
    } finally {
        saveBtn.innerHTML = originalHTML;
        saveBtn.disabled = false;
    }
}

function resetSettings() {
    for (const key in originalSettings) {
        const inputElement = document.getElementById(`input-${key}`);
        if (inputElement) inputElement.value = originalSettings[key];
    }
    showToast('Các thay đổi đã được hủy', 'info');
}

