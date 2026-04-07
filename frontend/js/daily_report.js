let myFixRequests = [];

$(document).ready(function () {
    const $monthSelect = $('#report-month');
    const $yearInput = $('#report-year');
    const $filterBtn = $('#report-filter-btn');

    if ($monthSelect.length === 0 || $yearInput.length === 0 || $filterBtn.length === 0) return;

    const now = new Date();
    const currentMonth = now.getMonth() + 1;
    const currentYear = now.getFullYear();

    $monthSelect.val(currentMonth);
    $yearInput.val(currentYear);

    async function initReportsPage() {
        try {
            await checkAuthAndGetUser();

            const month = $monthSelect.val();
            const year = $yearInput.val();

            await fetchMyFixRequests(month, year);
            await fetchAndRenderReports(month, year);

        } catch (error) {
            console.error("Lỗi khởi tạo:", error);
        }
    }

    $filterBtn.on('click', function () {
        const m = $monthSelect.val();
        const y = $yearInput.val();

        fetchMyFixRequests(m, y);
        fetchAndRenderReports(m, y);
    });

    initReportsPage();
});

//------- Call API--------
function fetchMyFixRequests(month, year) {
    return $.ajax({
        url: '/fix-attendance-requests/my-requests',
        type: 'GET',
        data: {
            month: month,
            year: year
        },
        success: function (response) {

            myFixRequests = response.data || [];
            console.log("Đã cập nhật mảng myFixRequests:", myFixRequests);

        },
        error: function (xhr) {
            if (typeof showToast === "function") {
                showToast("Không thể tải danh sách yêu cầu sửa công", "danger");
            } else {
                console.error("Lỗi tải yêu cầu sửa công:", xhr);
            }
        }
    });
}

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

function submitFixRequest() {
    const workDate = $('#modal-work-date').val();
    const checkIn = $('#modal-check-in').val();
    const checkOut = $('#modal-check-out').val();
    const reason = $('#modal-reason').val();

    if (!checkIn || !checkOut || !reason) {
        alert("Vui lòng nhập đầy đủ thông tin!");
        return;
    }

    const payload = {
        work_date: workDate,
        requested_check_in: `${checkIn}:00`,
        requested_check_out: `${checkOut}:00`,
        reason: reason
    };

    $.ajax({
        url: '/fix-attendance-requests',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(payload),
        beforeSend: function () {

            $('button[onclick="submitFixRequest()"]').prop('disabled', true).text('Đang gửi...');
        },
        success: function (res) {
            showToast("Gửi yêu cầu thành công!", "success");
            const modalElement = document.getElementById('fixAttendanceModal');
            bootstrap.Modal.getInstance(modalElement).hide();
            // Reset form
            $('#modal-reason').val('');
        },
        error: function (xhr) {
            const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : "Không thể gửi yêu cầu";
            showToast("Lỗi: " + errorMsg, "danger");
            console.log(xhr.responseJSON)
        },
        complete: function () {
            $('button[onclick="submitFixRequest()"]').prop('disabled', false).html('Gửi yêu cầu');
        }
    });
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

    document.getElementById('report-total-work-hours').innerText = `${totalHours}h`;
    document.getElementById('report-total-late').innerText = `${totalLate}p`;
    document.getElementById('report-total-early').innerText = `${totalEarly}p`;
    document.getElementById('report-total-ot').innerText = `${totalOT}p`;
}

/**
 * Render bảng chi tiết
 */

function getFixStatus(item) {
    const requestFound = myFixRequests.find(req => req.work_date === item.work_date);

    const isRequested = !!requestFound;
    const hasLack = item.lack_minutes > 0;

    return {
        canFix: hasLack && !isRequested,
        isRequested: isRequested,
        requestInfo: requestFound
    };
}

function renderTable(data) {
    const tbody = document.getElementById('reports-tbody');

    if (!data || data.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" class="empty-state-cell">Không có dữ liệu công số hàng ngày</td></tr>`;
        return;
    }


    const rowsHtml = data.map(item => {
        const d = new Date(item.work_date);
        const displayDate = !isNaN(d)
            ? `${d.getDate().toString().padStart(2, '0')}/${(d.getMonth() + 1).toString().padStart(2, '0')}`
            : item.work_date;

        const status = getFixStatus(item);

        let actionHtml = '';

        if (status.canFix) {
            actionHtml = `
                <div class="dropdown">
                    <button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="dropdown">
                        <i class="fa-solid fa-bars"></i>
                    </button>
                    <ul class="dropdown-menu shadow">
                        <li>
                            <a class="dropdown-item" href="javascript:void(0)" 
                               onclick="openFixModal('${item.work_date}', '${item.check_in || ''}', '${item.check_out || ''}')">
                               <i class="fa-solid fa-file-signature me-2 text-primary"></i>Tạo yêu cầu sửa công
                            </a>
                        </li>
                    </ul>
                </div>`;
        } else if (status.isRequested) {

            const s = status.requestInfo.status.toLowerCase();
            const config = {
                'approved': { class: 'bg-success text-white', text: 'Chấp nhận' },
                'rejected': { class: 'bg-danger text-white', text: 'Từ chối' },
                'pending': { class: 'bg-warning text-dark', text: 'Chờ sửa công' }
            };

            const res = config[s] || config['pending'];

            actionHtml = `
                <span class="badge ${res.class}" style="font-size: 0.65rem; min-width: 80px;">
                   ${res.text}
                </span>`
        }

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
                <td>${actionHtml}</td>
            </tr>
        `;
    }).join('');

    tbody.innerHTML = rowsHtml;
}

// Modal fix attendance
function openFixModal(date, currentIn, currentOut) {
    $('#modal-work-date').val(date);
    $('#display-date').text(date);

    $('#modal-check-in').val(currentIn ? currentIn.substring(0, 5) : "");
    $('#modal-check-out').val(currentOut ? currentOut.substring(0, 5) : "");

    const modalElement = document.getElementById('fixAttendanceModal');
    const myModal = bootstrap.Modal.getOrCreateInstance(modalElement);
    myModal.show();
}