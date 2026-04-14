let currentPage = 1;
let currentLimit = 30;

$(document).ready(function () {
    checkAuthAndGetUser();
    loadPayrollData();
    checkPayrollPeriodStatus();

    $('#limit-select').on('change', function () {
        currentLimit = $(this).val();
        currentPage = 1;
        loadPayrollData();
    });
});

function loadPayrollData() {
    const payrollBody = $('#payroll-tbody');

    payrollBody.html('<tr><td colspan="8" class="empty-state-cell">Đang tải dữ liệu...</td></tr>');

    $.ajax({
        url: `/payroll/monthly-reports`,
        type: 'GET',
        data: {
            page: currentPage,
            limit: currentLimit
        },
        success: function (res) {
            if (res.status === 1000) {
                renderTable(res.data);
                renderPagination(res.pagination);
            } else {
                payrollBody.html('<tr><td colspan="8">Không có dữ liệu</td></tr>');
            }
        },
        error: function () {
            payrollBody.html('<tr><td colspan="8" class="text-danger">Lỗi API</td></tr>');
        }
    });
}

function renderTable(data) {
    const payrollBody = $('#payroll-tbody');

    if (!data || data.length === 0) {
        payrollBody.html('<tr><td colspan="12">Không có dữ liệu</td></tr>');
        return;
    }

    const rows = data.map(item => {
        return `
        <tr>
            <td>${item.id}</td>
            <td>${item.employee_id}</td>
            <td>${item.employee_name}</td>
            <td>${item.email}</td>
            <td>${item.department_id}</td>
            <td>${formatDateNoYear(item.period_start)} - ${formatDateNoYear(item.period_end)}</td>
            <td>${formatMinutes(item.standard_work_minutes)}</td>
            <td class="${item.lack_minutes > 0 ? 'text-danger fw-bold' : ''}">${item.lack_minutes}</td>
            <td>${formatMinutes(item.estimated_minutes)}</td>
            <td>${item.actual_work_days}</td>
            <td>${item.paid_leave_days}</td>
            <td>${item.unpaid_leave_days}</td>
        </tr>
        `;
    }).join('');

    payrollBody.html(rows);
}

function renderPagination(pagination) {
    const paginationContainer = $('#pagination');
    paginationContainer.empty();

    const totalPages = pagination.total_pages;
    const currentPageNumber = pagination.page;

    $('#pagination-info').text(`Trang ${currentPageNumber}/${totalPages} - Tổng ${pagination.total_elements} bản ghi`);

    let html = '';

    html += `
      <li class="page-item ${currentPageNumber === 1 ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="changePage(${currentPageNumber - 1})">«</a>
      </li>
    `;

    for (let i = 1; i <= totalPages; i++) {
        html += `
          <li class="page-item ${i === currentPageNumber ? 'active' : ''}">
            <a class="page-link" href="#" onclick="changePage(${i})">${i}</a>
          </li>
        `;
    }

    html += `
      <li class="page-item ${currentPageNumber === totalPages ? 'disabled' : ''}">
        <a class="page-link" href="#" onclick="changePage(${currentPageNumber + 1})">»</a>
      </li>
    `;

    paginationContainer.html(html);
}

function changePage(page) {
    currentPage = page;
    loadPayrollData();
}

function formatMinutes(minutes) {
    if (!minutes) return '0h';
    const hours = Math.floor(minutes / 60);
    const remainder = minutes % 60;
    return `${hours}h ${remainder}m`;
}

function formatDateNoYear(dateStr) {
    if (!dateStr) return '';
    const parts = dateStr.split('-');
    return `${parts[2]}/${parts[1]}`;
}

function lockPayrollPeriod() {
    const confirmLock = confirm(
        "Sau khi khóa kỳ công sẽ không thể hoàn tác.\n\nBạn có chắc chắn muốn tiếp tục?"
    );

    if (!confirmLock) return;

    $.ajax({
        url: `/payroll/lock-period?month=${new Date().getMonth() + 1}&year=${new Date().getFullYear()}&closing_day=${new Date().getDate()}`,
        type: 'POST',

        success: function (res) {
            if (res.status === 1000) {
                showToast("Đã khóa kỳ công thành công!", "success");
            } else {
                showToast("Khóa kỳ công thất bại!", "danger");
            }
            $('.btn-lock').prop('disabled', true).text('Đã khóa');
        },
        error: function (xhr) {
            let msg = "Lỗi khi khóa kỳ công!";
            if (xhr.responseJSON?.detail) {
                msg = xhr.responseJSON.detail;
            }
            showToast(msg, "danger");
        }
    });
}

function checkPayrollPeriodStatus() {
    const month = $('#filterMonth').val() || (new Date().getMonth() + 1);
    const year = $('#filterYear').val() || new Date().getFullYear();

    $.ajax({
        url: `/payroll/period-control`,
        type: 'GET',
        data: { month: month, year: year },
        success: function (res) {

            if (res.data) {
                $('.btn-lock')
                    .prop('disabled', true)
                    .removeClass('btn-outline-warning')
                    .addClass('btn-secondary')
                    .html('<i class="fa-solid fa-lock me-1"></i> Đã khóa công');
            } else {
                $('.btn-lock')
                    .prop('disabled', false)
                    .removeClass('btn-secondary')
                    .addClass('btn-outline-warning')
                    .html('<i class="fa-solid fa-lock me-1"></i> Khóa kỳ công');
            }
        },
        error: function (xhr) {
            console.error("Lỗi check kỳ công:", xhr);
        }
    });
}

async function exportExcel() {
    const token = localStorage.getItem('access_token');

    try {
        const response = await fetch(`${API_URL}/payroll/export-excel`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Không thể tải file');
        }

        const disposition = response.headers.get('Content-Disposition');
        let fileName = 'bang-cong.xlsx';

        if (disposition && disposition.includes('filename=')) {
            fileName = disposition
                .split('filename=')[1]
                .replace(/"/g, '');
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        a.remove();

        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error(error);
        alert('Xuất file thất bại!');
    }
}

/** Call API chốt công */
function calculate_batch_payroll(btnElement) {
    const today = new Date();
    const currentDay = today.getDate();
    const month = today.getMonth() + 1;
    const year = today.getFullYear();

    const closingDay = currentDay;

    if (currentDay < 18 || currentDay > 20) {
        const proceed = confirm(`CẢNH BÁO: Hôm nay là ngày ${currentDay}. Thông thường việc chốt công chỉ diễn ra từ ngày 18 đến ngày 20 hàng tháng.\n\nBạn có chắc chắn muốn tiếp tục chốt công vào ngày này không?`);
        if (!proceed) return;
    }

    const $btn = $(btnElement || event.target);
    const originalClass = "btn btn-outline-primary btn-sm shadow-sm";
    const loadingClass = "btn-primary btn-sm disabled";

    $btn.attr('class', loadingClass)
        .html('<span class="spinner-border spinner-border-sm me-1"></span> Đang xử lý...');

    $.ajax({
        url: '/payroll/calculate-batch',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            month: parseInt(month),
            year: parseInt(year),
            closing_day: parseInt(closingDay)
        }),
        success: function (response) {
            if (response.status === 1000) {
                showToast("Tính toán bảng công thành công!", "success");
                loadPayrollData();
            } else {
                showToast("Có lỗi: " + response.message, "danger");
            }
        },
        error: function (xhr) {
            const errorMsg = xhr.responseJSON ? xhr.responseJSON.message : "Lỗi hệ thống";
            showToast("Không thể chốt công: " + errorMsg, "danger");
        },
        complete: function () {
            $btn.attr('class', originalClass).html('Chốt công');
        }
    });
}