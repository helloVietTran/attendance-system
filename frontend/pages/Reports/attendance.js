/**
 * Khởi tạo trang Chấm Công
 */
async function initAttendancePage() {
    console.log("Khởi tạo trang Chấm Công...");

    try {
        // Kiểm tra xem các phần tử DOM có tồn tại không
        const employeeSelect = document.getElementById('attendance-employee-select');
        const filterBtn = document.getElementById('attendance-filter-btn');
        const monthSelect = document.getElementById('attendance-month');
        const yearInput = document.getElementById('attendance-year');

        if (!employeeSelect || !filterBtn) {
            console.error('Không tìm thấy các phần tử DOM cần thiết');
            return;
        }

        console.log('Các phần tử DOM được tìm thấy');

        // Load danh sách nhân viên
        await loadEmployeeList('attendance-employee-select');

        // Setup event listeners
        filterBtn.addEventListener('click', async () => {
            console.log('Nút Tìm kiếm được ấn');
            await loadAttendanceLogs();
        });

        // Set mặc định tháng/năm hiện tại
        const now = new Date();
        if (monthSelect) {
            monthSelect.value = now.getMonth() + 1;
        }
        if (yearInput) {
            yearInput.value = now.getFullYear();
        }

        console.log('Trang Chấm Công khởi tạo thành công');
    } catch (error) {
        console.error('Lỗi khởi tạo trang Chấm Công:', error);
    }
}

/**
 * Load danh sách nhân viên
 */
async function loadEmployeeList(selectElementId) {
    try {
        console.log('Load danh sách nhân viên...');
        const resp = await fetch('/api/v1/employees/');

        if (!resp.ok) {
            console.error('Lỗi API:', resp.status, resp.statusText);
            return;
        }

        const result = await resp.json();
        const employees = result.data || [];
        const select = document.getElementById(selectElementId);

        if (!select) {
            console.error('Không tìm thấy select element:', selectElementId);
            return;
        }

        console.log(`Tải được ${employees.length} nhân viên`);

        employees.forEach(emp => {
            const option = document.createElement('option');
            option.value = emp.id;
            option.textContent = `${emp.name} (${emp.employee_code || emp.id})`;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('Lỗi tải danh sách nhân viên:', error);
    }
}

/**
 * Load log chấm công
 */
async function loadAttendanceLogs() {
    try {
        const employeeSelect = document.getElementById('attendance-employee-select');
        const monthSelect = document.getElementById('attendance-month');
        const yearInput = document.getElementById('attendance-year');

        const employeeId = employeeSelect?.value;
        const month = monthSelect?.value;
        const year = yearInput?.value;

        if (!employeeId) {
            alert('Vui lòng chọn nhân viên');
            return;
        }

        console.log(`Load log chấm công: emp_id=${employeeId}, month=${month}, year=${year}`);

        const resp = await fetch(`/api/v1/attendance/logs/${employeeId}?month=${month}&year=${year}`);

        if (!resp.ok) {
            console.error('Lỗi API:', resp.status, resp.statusText);
            alert('Không thể tải dữ liệu chấm công');
            return;
        }

        const result = await resp.json();
        const logs = result.data || [];

        console.log(`Tải được ${logs.length} log chấm công`);

        // Hiển thị log
        displayAttendanceLogs(logs);

        // Cập nhật thống kê
        updateAttendanceStats(logs);
    } catch (error) {
        console.error('Lỗi load log chấm công:', error);
        alert('Lỗi khi tải dữ liệu chấm công: ' + error.message);
    }
}

/**
 * Hiển thị log chấm công trong bảng
 */
function displayAttendanceLogs(logs) {
    const tbody = document.getElementById('attendance-logs-tbody');

    if (!tbody) {
        console.error('Không tìm thấy attendance-logs-tbody');
        return;
    }

    if (!logs || logs.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="padding: 20px; text-align: center; color: #888;">Không có dữ liệu chấm công</td></tr>';
        return;
    }

    tbody.innerHTML = logs.map(log => {
        const status = getAttendanceStatus(log);
        return `
        <tr style="border-bottom: 1px solid var(--border-color);">
            <td style="padding: 12px; color: var(--text-light);">${formatDateAttendance(log.log_date)}</td>
            <td style="padding: 12px; color: var(--text-light);">${log.shift_start} - ${log.shift_end}</td>
            <td style="padding: 12px; color: var(--text-light);">${log.checked_time || '--'}</td>
            <td style="padding: 12px; text-align: center;">
                ${status}
            </td>
        </tr>
        `;
    }).join('');
}

/**
 * Xác định trạng thái chấm công
 */
function getAttendanceStatus(log) {
    if (!log.checked_time) {
        return '<span style="color: #f44336; font-weight: bold;">❌ Không có dữ liệu</span>';
    }

    try {
        const shiftStart = new Date(`2000-01-01 ${log.shift_start}`);
        const checkedTime = new Date(`2000-01-01 ${log.checked_time}`);

        if (checkedTime <= shiftStart) {
            return '<span style="color: #4caf50; font-weight: bold;">✅ Đúng giờ</span>';
        } else {
            const diffMinutes = Math.round((checkedTime - shiftStart) / 60000);
            return `<span style="color: #ff9800; font-weight: bold;">⚠️ Muộn ${diffMinutes}p</span>`;
        }
    } catch (error) {
        console.error('Error parsing time:', error);
        return '<span style="color: #999;">--</span>';
    }
}

/**
 * Cập nhật thống kê chấm công
 */
function updateAttendanceStats(logs) {
    try {
        let totalDays = 0;
        let lateCount = 0;
        let earlyCount = 0;
        let noDataCount = 0;

        logs.forEach(log => {
            if (!log.checked_time) {
                noDataCount++;
            } else {
                totalDays++;

                const shiftStart = new Date(`2000-01-01 ${log.shift_start}`);
                const checkedTime = new Date(`2000-01-01 ${log.checked_time}`);

                if (checkedTime > shiftStart) {
                    lateCount++;
                }
            }
        });

        const totalDaysEl = document.getElementById('attendance-total-days');
        const lateCountEl = document.getElementById('attendance-late-count');
        const earlyCountEl = document.getElementById('attendance-early-count');
        const noDataCountEl = document.getElementById('attendance-no-data-count');

        if (totalDaysEl) totalDaysEl.textContent = totalDays;
        if (lateCountEl) lateCountEl.textContent = lateCount;
        if (earlyCountEl) earlyCountEl.textContent = earlyCount;
        if (noDataCountEl) noDataCountEl.textContent = noDataCount;
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

/**
 * Format ngày theo định dạng DD/MM/YYYY
 */
function formatDateAttendance(dateString) {
    try {
        const date = new Date(dateString);
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}/${month}/${year}`;
    } catch (error) {
        return dateString;
    }
}

/**
 * Format giờ từ chuỗi
 */
function formatTimeAttendance(timeString) {
    if (!timeString) return '--';
    return timeString.slice(0, 5); // HH:MM
}

