/**
 * Khởi tạo trang Báo Cáo Công
 */
async function initReportsPage() {
    // kiểm tra đăng nhập chưa
    await checkAuthAndGetUser();

    const monthSelect = document.getElementById('report-month');
    const yearInput = document.getElementById('report-year');
    const filterBtn = document.getElementById('report-filter-btn');

    if (!monthSelect || !yearInput || !filterBtn) return;

    // Set mặc định tháng/năm hiện tại vào Filter
    const now = new Date();
    const currentMonth = now.getMonth() + 1;
    const currentYear = now.getFullYear();

    monthSelect.value = currentMonth;
    yearInput.value = currentYear;

    // Sự kiện nút tìm kiếm
    filterBtn.addEventListener('click', () => {
        fetchAndRenderReports(monthSelect.value, yearInput.value);
    });

    // Chạy lần đầu khi load trang
    await fetchAndRenderReports(currentMonth, currentYear);
}

/**
 * Lấy dữ liệu từ API và render
 */
async function fetchAndRenderReports(month, year) {
    const user = JSON.parse(localStorage.getItem("user"));
    const employeeId = user?.id ?? null;

    const tbody = document.getElementById('reports-tbody');
    if (!tbody) return;

    if (!employeeId) {
        tbody.innerHTML = `<tr><td colspan="8" class="empty-state-cell" style="color: orange;">Không tìm thấy thông tin nhân viên trong bộ nhớ.</td></tr>`;
        return;
    }

    const apiUrl = `${API_URL}/attendance/daily-reports/${employeeId}?month=${month}&year=${year}`;
    
    try {
        tbody.innerHTML = `<tr><td colspan="8" class="empty-state-cell">Đang tải dữ liệu...</td></tr>`;

        const response = await fetch(apiUrl);
        const result = await response.json();

        // Kiểm tra status 1000 (theo logic backend của bạn)
        if (result.status === 1000 && result.data) {
            renderSummary(result.data);
            renderTable(result.data);
        } else {
            renderSummary([]); // Reset thông số về 0
            tbody.innerHTML = `<tr><td colspan="8" class="empty-state-cell">Không có dữ liệu cho thời gian này</td></tr>`;
        }
    } catch (error) {
        console.error('Error:', error);
        tbody.innerHTML = `<tr><td colspan="8" class="empty-state-cell" style="color: red;">Không thể kết nối máy chủ: ${error.message}</td></tr>`;
    }
}

/**
 * Render các thẻ Thống kê (Stat Cards)
 */
function renderSummary(data) {
    let totalWorkMinutes = 0;
    let totalLate = 0;
    let totalEarly = 0;
    let totalOT = 0;

    data.forEach(item => {
        totalWorkMinutes += (item.work_time_minutes || 0);
        totalLate += (item.late_arrive_minutes || 0);
        totalEarly += (item.leave_early_minutes || 0);
        totalOT += (item.overtime_minutes || 0);
    });

    const totalHours = (totalWorkMinutes / 60).toFixed(1);

    // Update UI (Dựa trên ID trong HTML của bạn)
    document.getElementById('report-total-work-hours').innerText = `${totalHours}h`;
    document.getElementById('report-total-late').innerText = `${totalLate}p`;
    document.getElementById('report-total-early').innerText = `${totalEarly}p`;
    document.getElementById('report-total-ot').innerText = `${totalOT}p`;
}

/**
 * Render bảng chi tiết
 */
function renderTable(data) {
    const tbody = document.getElementById('reports-tbody');
    
    if (!data || data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="empty-state-cell">Không có dữ liệu công số hàng ngày</td></tr>`;
        return;
    }

    const rowsHtml = data.map(item => {
        // Xử lý ngày hiển thị (VD: 2026-04-06 -> 06/04)
        const d = new Date(item.work_date);
        const displayDate = !isNaN(d) 
            ? `${d.getDate().toString().padStart(2, '0')}/${(d.getMonth() + 1).toString().padStart(2, '0')}`
            : item.work_date;
        
        return `
            <tr>
                <td style="font-weight: 500;">${displayDate}</td>
                <td>${item.check_in || '--:--'}</td>
                <td>${item.check_out || '--:--'}</td>
                <td>${item.work_time_minutes || 0}</td>
                <td class="${(item.late_arrive_minutes || 0) > 0 ? 'text-warning fw-bold' : ''}">${item.late_arrive_minutes || 0}</td>
                <td class="${(item.leave_early_minutes || 0) > 0 ? 'text-warning fw-bold' : ''}">${item.leave_early_minutes || 0}</td>
                <td class="${(item.lack_minutes || 0) > 0 ? 'text-danger fw-bold' : ''}">${item.lack_minutes || 0}</td>
                <td class="${(item.overtime_minutes || 0) > 0 ? 'text-success fw-bold' : ''}">${item.overtime_minutes || 0}</td>
            </tr>
        `;
    }).join('');

    tbody.innerHTML = rowsHtml;
}

// Khởi tạo khi trang sẵn sàng
document.addEventListener('DOMContentLoaded', initReportsPage);