let originalSettings = {};
let currentSettings = {};

const settingLabels = {
    'lunch_break_start': 'Giờ bắt đầu giờ ăn trưa',
    'lunch_break_end': 'Giờ kết thúc giờ ăn trưa',
    'annual_paid_leave_days': 'Số ngày phép năm',
    'maternity_leave_months': 'Số tháng phép thai sản',
    'max_attendance_correction_per_month': 'Số lần sửa công/tháng'
};

const settingDescriptions = {
    'lunch_break_start': 'Thời gian bắt đầu giờ ăn trưa (định dạng HH:mm)',
    'lunch_break_end': 'Thời gian kết thúc giờ ăn trưa (định dạng HH:mm)',
    'annual_paid_leave_days': 'Tổng số ngày phép được hưởng mỗi năm',
    'maternity_leave_months': 'Số tháng phép thai sản cho lao động nữ',
    'max_attendance_correction_per_month': 'Số lần tối đa được phép chỉnh sửa công mỗi tháng'
};

document.addEventListener('DOMContentLoaded', async function () {
    console.log('Settings page loaded');
    await initSettingsPage();
});

async function initSettingsPage() {
    await checkAuthAndGetUser();
    const user = JSON.parse(localStorage.getItem("user"));
    if (!user) {
        showAlert('Lỗi: Không tìm thấy thông tin người dùng', 'error');
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
        console.log('Loading settings from API...');
        const response = await fetchWithAuth(`${API_URL}/settings`);
        if (!response.ok) throw new Error(`API Error: ${response.status}`);
        const result = await response.json();
        console.log('API Response:', result);
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
            console.log('Settings loaded:', originalSettings);
            renderSettings(settingsArray);
        } else {
            throw new Error('Invalid API response format');
        }
    } catch (error) {
        console.error('Error loading settings:', error);
        container.innerHTML = `<div class="text-center" style="padding: 40px; color: red;"><i class="fa-solid fa-exclamation-triangle" style="font-size: 24px;"></i><p style="margin-top: 10px;">Lỗi: ${error.message}</p></div>`;
        showAlert('Lỗi khi tải cài đặt: ' + error.message, 'error');
    }
}

function renderSettings(settingsArray) {
    const container = document.getElementById('settings-container');
    let html = '<div style="display: grid; gap: 20px;">';
    settingsArray.forEach(setting => {
        if (setting && setting.key) {
            const label = settingLabels[setting.key] || setting.key;
            const description = settingDescriptions[setting.key] || setting.description || '';
            const inputType = setting.key.includes('lunch') ? 'time' : 'number';
            const value = setting.value || '';
            const min = inputType === 'number' ? 'min="0"' : '';
            html += `<div style="border: 1px solid #f0f0f0; border-radius: 8px; padding: 20px; background-color: #fafafa;"><div style="display: grid; grid-template-columns: 1fr 2fr; gap: 20px; align-items: center;"><div><label style="display: block; font-size: 14px; font-weight: 600; color: #262626; margin-bottom: 5px;"><i class="fa-solid fa-gear" style="margin-right: 8px; color: #007bff;"></i>${label}</label><p style="font-size: 12px; color: #999; margin: 0;">${description}</p></div><div><input type="${inputType}" id="input-${setting.key}" value="${value}" class="custom-input" ${min} /></div></div></div>`;
        }
    });
    html += '</div>';
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
        showAlert('Không có thay đổi để lưu', 'info');
        return;
    }
    console.log('Saving updates:', updates);
    const saveBtn = document.getElementById('save-settings-btn');
    const originalHTML = saveBtn.innerHTML;
    saveBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Đang lưu...';
    saveBtn.disabled = true;
    try {
        const response = await fetchWithAuth(`${API_URL}/settings`, { method: 'PUT', body: JSON.stringify(updates) });
        if (!response.ok) throw new Error(`API Error: ${response.status}`);
        const result = await response.json();
        console.log('Save response:', result);
        if (result.status === 1000) {
            updates.forEach(update => { originalSettings[update.key] = update.value; });
            showAlert('Cài đặt đã được lưu thành công', 'success');
        } else {
            throw new Error(result.detail || 'Lỗi không xác định');
        }
    } catch (error) {
        console.error('Error saving settings:', error);
        showAlert('Lỗi khi lưu cài đặt: ' + error.message, 'error');
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
    showAlert('Các thay đổi đã được hủy', 'info');
}

function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    let alertClass = 'alert-info';
    let icon = 'fa-info-circle';
    if (type === 'error') {
        alertClass = 'alert-danger';
        icon = 'fa-circle-exclamation';
    } else if (type === 'success') {
        alertClass = 'alert-success';
        icon = 'fa-circle-check';
    }
    const alertHtml = `<div class="alert ${alertClass} alert-dismissible fade show" role="alert" style="display: flex; align-items: center; gap: 10px;"><i class="fa-solid ${icon}"></i><span>${message}</span><button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button></div>`;
    alertContainer.innerHTML = alertHtml;
    if (type !== 'error') {
        setTimeout(() => {
            const alert = alertContainer.querySelector('.alert');
            if (alert) alert.remove();
        }, 5000);
    }
}