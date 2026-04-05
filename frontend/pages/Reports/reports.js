/**
 * Khởi tạo trang Báo Cáo Công
 */
async function initReportsPage() {
    console.log("Khởi tạo trang Báo Cáo Công...");

    try {
        // Kiểm tra xem các phần tử DOM có tồn tại không
        const employeeSelect = document.getElementById('report-employee-select');
        const filterBtn = document.getElementById('report-filter-btn');
        const exportBtn = document.getElementById('report-export-btn');
        const monthSelect = document.getElementById('report-month');
        const yearInput = document.getElementById('report-year');

        if (!employeeSelect || !filterBtn) {
            console.error('Không tìm thấy các phần tử DOM cần thiết');
            return;
        }

        console.log('Các phần tử DOM được tìm thấy');

        // Load danh sách nhân viên
        await loadEmployeeListForReports('report-employee-select');

        // Setup event listeners
        filterBtn.addEventListener('click', async () => {
            console.log('Nút Tìm kiếm được ấn');
            await loadDailyReports();
        });

        if (exportBtn) {
            exportBtn.addEventListener('click', async () => {
                console.log('Nút Xuất Excel được ấn');
                await exportReportsToExcel();
            });
        }

        // Set mặc định tháng/năm hiện tại
        const now = new Date();
        if (monthSelect) {
            monthSelect.value = now.getMonth() + 1;
        }
        if (yearInput) {
            yearInput.value = now.getFullYear();
        }

        console.log('Trang Báo Cáo Công khởi tạo thành công');
    } catch (error) {
        console.error('Lỗi khởi tạo trang Báo Cáo Công:', error);
    }
}

/**
 * Load danh sách nhân viên cho báo cáo
 */
async function loadEmployeeListForReports(selectElementId) {
    try {
        console.log('Load danh sách nhân viên cho báo cáo...');
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
 * Load báo cáo công hàng ngày
 */
async function loadDailyReports() {
    try {
        const employeeSelect = document.getElementById('report-employee-select');
        const monthSelect = document.getElementById('report-month');
        const yearInput = document.getElementById('report-year');

        const employeeId = employeeSelect?.value;
        const month = monthSelect?.value;
        const year = yearInput?.value;

        if (!employeeId) {
            alert('Vui lòng chọn nhân viên');
            return;
        }

        console.log(`Load báo cáo công: emp_id=${employeeId}, month=${month}, year=${year}`);

        const resp = await fetch(`/api/v1/attendance/daily-reports/${employeeId}?month=${month}&year=${year}`);

        if (!resp.ok) {
            console.error('Lỗi API:', resp.status, resp.statusText);
            alert('Không thể tải dữ liệu báo cáo công');
            return;
        }

        const result = await resp.json();
        const reports = result.data || [];

        console.log(`Tải được ${reports.length} báo cáo công`);

        // Hiển thị báo cáo
        displayDailyReports(reports);

        // Cập nhật thống kê
        updateReportStats(reports);
    } catch (error) {
        console.error('Lỗi load báo cáo công:', error);
        alert('Lỗi khi tải dữ liệu báo cáo công: ' + error.message);
    }
}

/**
 * Hiển thị báo cáo công trong bảng
 */
function displayDailyReports(reports) {
    const tbody = document.getElementById('reports-tbody');

    if (!tbody) {
        console.error('Không tìm thấy reports-tbody');
        return;
    }

    if (!reports || reports.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" style="padding: 20px; text-align: center; color: #888;">Không có dữ liệu báo cáo công</td></tr>';
        return;
    }

    tbody.innerHTML = reports.map(report => {
        return `
        <tr style="border-bottom: 1px solid var(--border-color);">
            <td style="padding: 10px; text-align: center; color: var(--text-light);">${formatDateReports(report.work_date)}</td>
            <td style="padding: 10px; text-align: center; color: var(--text-light);">${report.check_in || '--'}</td>
            <td style="padding: 10px; text-align: center; color: var(--text-light);">${report.check_out || '--'}</td>
            <td style="padding: 10px; text-align: center; color: var(--text-light); font-weight: bold;">${(report.work_time_minutes / 60).toFixed(1)}</td>
            <td style="padding: 10px; text-align: center; color: ${report.late_arrive_minutes > 0 ? '#ff9800' : 'var(--text-light)'};">${report.late_arrive_minutes}</td>
            <td style="padding: 10px; text-align: center; color: ${report.leave_early_minutes > 0 ? '#ff9800' : 'var(--text-light)'};">${report.leave_early_minutes}</td>
            <td style="padding: 10px; text-align: center; color: ${report.lack_minutes > 0 ? '#f44336' : 'var(--text-light)'};">${report.lack_minutes}</td>
            <td style="padding: 10px; text-align: center; color: ${report.overtime_minutes > 0 ? '#4caf50' : 'var(--text-light)'};">${report.overtime_minutes}</td>
        </tr>
        `;
    }).join('');
}

/**
 * Cập nhật thống kê báo cáo công
 */
function updateReportStats(reports) {
    try {
        if (!reports || reports.length === 0) {
            document.getElementById('report-total-work-hours').textContent = '0h';
            document.getElementById('report-total-late').textContent = '0p';
            document.getElementById('report-total-early').textContent = '0p';
            document.getElementById('report-total-lack').textContent = '0p';
            document.getElementById('report-total-ot').textContent = '0p';
            return;
        }

        let totalWorkMinutes = 0;
        let totalLateMinutes = 0;
        let totalEarlyMinutes = 0;
        let totalLackMinutes = 0;
        let totalOTMinutes = 0;

        reports.forEach(report => {
            totalWorkMinutes += report.work_time_minutes || 0;
            totalLateMinutes += report.late_arrive_minutes || 0;
            totalEarlyMinutes += report.leave_early_minutes || 0;
            totalLackMinutes += report.lack_minutes || 0;
            totalOTMinutes += report.overtime_minutes || 0;
        });

        const totalWorkHours = (totalWorkMinutes / 60).toFixed(1);

        const workHoursEl = document.getElementById('report-total-work-hours');
        const lateEl = document.getElementById('report-total-late');
        const earlyEl = document.getElementById('report-total-early');
        const lackEl = document.getElementById('report-total-lack');
        const otEl = document.getElementById('report-total-ot');

        if (workHoursEl) workHoursEl.textContent = `${totalWorkHours}h`;
        if (lateEl) lateEl.textContent = `${totalLateMinutes}p`;
        if (earlyEl) earlyEl.textContent = `${totalEarlyMinutes}p`;
        if (lackEl) lackEl.textContent = `${totalLackMinutes}p`;
        if (otEl) otEl.textContent = `${totalOTMinutes}p`;
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

/**
 * Xuất báo cáo công ra Excel/CSV
 */
async function exportReportsToExcel() {
    try {
        const employeeSelect = document.getElementById('report-employee-select');
        const monthSelect = document.getElementById('report-month');
        const yearInput = document.getElementById('report-year');

        const employeeId = employeeSelect?.value;
        const month = monthSelect?.value;
        const year = yearInput?.value;

        if (!employeeId) {
            alert('Vui lòng chọn nhân viên để xuất báo cáo');
            return;
        }

        console.log('Xuất báo cáo công...');

        // Lấy dữ liệu hiện tại từ bảng
        const tbody = document.getElementById('reports-tbody');
        const rows = tbody?.querySelectorAll('tr') || [];

        if (rows.length === 0 || rows[0].querySelector('td')?.textContent.includes('Không có dữ liệu')) {
            alert('Không có dữ liệu để xuất');
            return;
        }

        // Tạo CSV content
        let csvContent = 'Báo Cáo Công\n';
        csvContent += `Tháng ${month}/${year}\n\n`;
        csvContent += 'Ngày,Check In,Check Out,Giờ làm (phút),Đi muộn (phút),Về sớm (phút),Thiếu (phút),OT (phút)\n';

        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length === 8) {
                const rowData = Array.from(cells).map(cell => {
                    // Escape commas and quotes
                    const text = cell.textContent.trim();
                    return text.includes(',') ? `"${text}"` : text;
                }).join(',');
                csvContent += rowData + '\n';
            }
        });

        // Tạo file download
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        const url = URL.createObjectURL(blob);

        link.setAttribute('href', url);
        link.setAttribute('download', `bao_cao_cong_${month}_${year}.csv`);
        link.style.visibility = 'hidden';

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        console.log('Xuất báo cáo thành công');
        alert('Xuất báo cáo thành công');
    } catch (error) {
        console.error('Lỗi xuất báo cáo:', error);
        alert('Lỗi khi xuất báo cáo: ' + error.message);
    }
}

/**
 * Format ngày theo định dạng DD/MM/YYYY
 */
function formatDateReports(dateString) {
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
function formatTimeReports(timeString) {
    if (!timeString) return '--';
    return timeString.slice(0, 5); // HH:MM
}
