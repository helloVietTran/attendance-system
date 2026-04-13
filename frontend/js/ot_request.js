document.addEventListener("DOMContentLoaded", function () {

    // const userRole = localStorage.getItem("user")?.role; 

    // const adminRoles = ["ADMIN", "HR"];

    // if (adminRoles.includes(userRole)) {
    //     const adminTab = document.getElementById("admin-ot-tab-item");
    //     if (adminTab) {
    //         adminTab.classList.remove("d-none");
    //     }
    // }
    const adminTab = document.getElementById("admin-ot-tab-item");
    adminTab.classList.remove("d-none");
});


$(document).ready(function () {
    loadMyOTRequests();

    $('button[data-bs-toggle="tab"]').on('shown.bs.tab', function (e) {
        const targetId = $(e.target).attr('data-bs-target');

        if (targetId === '#my-request') {
            // Nếu quay lại tab "Của tôi" -> Tải lại danh sách cá nhân
            loadMyOTRequests();
        }
        else if (targetId === '#manage-request') {
            // Nếu nhấn sang tab "Quản lý" -> Tải danh sách toàn bộ (Admin/HR)
            loadAdminOTRequests(1);
        }
    });

    $('#addOTForm').on('submit', function (e) {
        e.preventDefault();
        createOTRequest();
    });
});

/**
 * Lấy danh sách yêu cầu OT của cá nhân
 */
function loadMyOTRequests() {
    const userData = JSON.parse(localStorage.getItem("user") || "{}");
    const employeeId = userData.id;
    const tbody = $('#my-ot-requests-tbody');

    if (!employeeId) return;

    $.ajax({
        url: `/overtimes/me`,
        type: 'GET',
        success: function (response) {
            if (response.status === 1000 && Array.isArray(response.data)) {
                renderOTTable(response.data);
            } else {
                tbody.html('<tr><td colspan="7" class="text-center">Chưa có yêu cầu OT nào.</td></tr>');
            }
        },
        error: function () {
            tbody.html('<tr><td colspan="7" class="text-center text-danger">Lỗi tải dữ liệu.</td></tr>');
        }
    });
}

function renderOTTable(data) {
    const tbody = $('#ot-requests-body');

    if (!data || data.length === 0) {
        tbody.html('<tr><td colspan="7" class="empty-state-cell text-center">Bạn chưa có yêu cầu OT nào.</td></tr>');
        return;
    }

    const rows = data.map(item => {
        // Xử lý Badge trạng thái (Khớp với dữ liệu "approved", "pending", "rejected" từ API)
        let statusBadge = '';
        const status = item.status.toUpperCase(); // Chuẩn hóa để so sánh

        switch (status) {
            case 'PENDING':
                statusBadge = '<span class="badge bg-warning text-dark"><i class="fa-solid fa-clock me-1"></i>Chờ duyệt</span>';
                break;
            case 'APPROVED':
                statusBadge = '<span class="badge bg-success"><i class="fa-solid fa-check-circle me-1"></i>Đã duyệt</span>';
                break;
            case 'REJECTED':
                statusBadge = '<span class="badge bg-danger"><i class="fa-solid fa-circle-xmark me-1"></i>Từ chối</span>';
                break;
            default:
                statusBadge = `<span class="badge bg-secondary">${item.status}</span>`;
        }

        // Mapping loại OT
        const otTypeMap = {
            'normal_day': 'Ngày thường',
            'weekend_day': 'Cuối tuần',
            'holiday_day': 'Ngày lễ'
        };
        const otTypeLabel = otTypeMap[item.ot_type] || item.ot_type;

        return `
            <tr>
                <td>${item.work_date}</td>
                <td>
                    ${item.start_time.substring(0, 5)} - ${item.end_time.substring(0, 5)}
                </td>
                <td><span class="small">${otTypeLabel}</span></td>
                <td>${item.actual_work_time}</td>
                <td><span class="fw-bold text-dark">x${item.multiplier}</span></td>
                <td>
                    <div class="text-truncate" style="max-width: 150px;" title="${item.reason || ''}">
                        ${item.reason || '...'}
                    </div>
                </td>
                <td>${statusBadge}</td>
                <td class="text-center">
                    ${status === 'PENDING' ?
                `<button class="btn btn-sm btn-outline-danger" onclick="deleteOTRequest(${item.id})">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>` :
                `<i class="fa-solid fa-lock text-muted" title="Đã xử lý - Không thể xóa"></i>`
            }
                </td>
            </tr>
        `;
    }).join('');

    tbody.html(rows);
}


// Helper badge
function getStatusBadge(status) {
    status = status.toUpperCase();
    if (status === 'APPROVED') return '<span class="badge bg-success">Đã duyệt</span>';
    if (status === 'REJECTED') return '<span class="badge bg-danger">Từ chối</span>';
    return '<span class="badge bg-warning text-dark">Chờ duyệt</span>';
}

//  Hàm load dữ liệu cho Admin
function loadAdminOTRequests(page = 1) {
    const search = $('#adminSearchName').val();
    const status = $('#adminFilterStatus').val();
    const month = new Date().getMonth() + 1;
    const year = new Date().getFullYear();

    $.ajax({
        url: `/overtimes/all`,
        type: 'GET',
        data: { page, limit: 10, search, status, month, year },
        success: function (response) {
            renderAdminOTTable(response.data);
            renderPagination(response.pagination, 'admin-ot-pagination', loadAdminOTRequests);
        }
    });
}

// Hàm render bảng cho Admin
function renderAdminOTTable(data) {
    const tbody = $('#admin-ot-tbody');
    if (!data || data.length === 0) {
        tbody.html('<tr><td colspan="7" class="text-center py-4">Không tìm thấy yêu cầu nào.</td></tr>');
        return;
    }

    const rows = data.map(item => {
        const isPending = item.status.toUpperCase() === 'PENDING';

        return `
            <tr>
                <td>
                    <div class="fw-bold">${item.employee_name || 'N/A'}</div>
                    <small class="text-muted">ID: ${item.employee_id}</small>
                </td>
                <td>${item.work_date}</td>
                <td>${item.start_time.substring(0, 5)} - ${item.end_time.substring(0, 5)}</td>
                <td>x${item.multiplier}</td>
                <td><small title="${item.reason}">${item.reason || ''}</small></td>
                <td>${getStatusBadge(item.status)}</td>
                <td class="text-center">
                    ${isPending ? `
                        <div class="btn-group">
                            <button class="btn btn-sm btn-success" onclick="updateOTStatus(${item.id}, 'approved')" title="Duyệt">
                                <i class="fa-solid fa-check"></i>
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="updateOTStatus(${item.id}, 'rejected')" title="Từ chối">
                                <i class="fa-solid fa-xmark"></i>
                            </button>
                        </div>
                    ` : `<small class="text-muted">Đã xử lý</small>`}
                </td>
            </tr>
        `;
    }).join('');
    tbody.html(rows);
}

//  Hàm gọi API Duyệt/Từ chối
function updateOTStatus(otId, newStatus) {
    const confirmMsg = newStatus === 'APPROVED' ? "Xác nhận DUYỆT đơn OT này?" : "Xác nhận TỪ CHỐI đơn OT này?";
    if (!confirm(confirmMsg)) return;

    $.ajax({
        url: `/overtimes/${otId}/status`,
        type: 'PATCH',
        contentType: 'application/json',
        data: JSON.stringify({ status: newStatus }),
        success: function (response) {
            showToast("Cập nhật trạng thái thành công", "success");
            loadAdminOTRequests();
        },
        error: function (xhr) {
            showToast(xhr.responseJSON?.detail || "Lỗi khi cập nhật", "danger");
        }
    });
}

/**
 * Tạo yêu cầu OT mới
 */
function createOTRequest() {
    const workDate = $('input[name="work_date"]').val();
    const startTime = $('input[name="start_time"]').val();
    const endTime = $('input[name="end_time"]').val();
    const otType = $('select[name="ot_type"]').val();
    const reason = $('textarea[name="reason"]').val().trim();

    if (!workDate || !startTime || !endTime) {
        showToast("Vui lòng điền đầy đủ ngày và giờ", "danger");
        return;
    }

    const payload = {
        work_date: workDate,     // YYYY-MM-DD
        start_time: startTime,   // HH:mm
        end_time: endTime,       // HH:mm
        reason: reason || null   // Optional
    };

    $.ajax({
        url: `/overtimes/`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(payload),
        success: function (response) {
            showToast("Gửi yêu cầu OT thành công!", "success");

            // Đóng modal và reset form
            const modalElement = document.getElementById('addOTModal');
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            modalInstance.hide();
            $('#addOTForm')[0].reset();

            // Reload danh sách ở tab "Yêu cầu của tôi"
            loadMyOTRequests();
        },
        error: function (xhr) {
            let errorMsg = "Không thể gửi yêu cầu";
            if (xhr.responseJSON && xhr.responseJSON.detail) {

                errorMsg = xhr.responseJSON.detail;
            }
            showToast(errorMsg, "danger");
            console.error("Lỗi tạo OT:", xhr);
        }
    });
}

/**
 * Xóa yêu cầu OT (chỉ khi đang PENDING)
 */
function deleteOTRequest(id) {
    if (!confirm("Bạn có chắc chắn muốn xóa yêu cầu này?")) return;

    $.ajax({
        url: `/overtimes/${id}`,
        type: 'DELETE',
        success: function () {
            showToast("Đã xóa yêu cầu", "success");
            loadMyOTRequests();
        },
        error: function () {
            showToast("Không thể xóa yêu cầu này", "danger");
        }
    });
}

function renderPagination(metadata, containerId, loadFunction) {
    const $container = $(`#${containerId}`);
    if (!metadata || metadata.total_pages <= 1) {
        $container.html('');
        return;
    }

    const { page, total_pages, total_elements } = metadata;

    let html = `
        <div class="small text-muted">
            Hiển thị trang <b>${page}</b> / <b>${total_pages}</b> (Tổng <b>${total_elements}</b> bản ghi)
        </div>
        <nav>
            <ul class="pagination pagination-sm mb-0">
                <li class="page-item ${page === 1 ? 'disabled' : ''}">
                    <a class="page-link" href="javascript:void(0)" onclick="${page > 1 ? `${loadFunction.name}(${page - 1})` : ''}">
                        <i class="fa-solid fa-chevron-left"></i>
                    </a>
                </li>
    `;

    for (let i = 1; i <= total_pages; i++) {
        html += `
            <li class="page-item ${i === page ? 'active' : ''}">
                <a class="page-link" href="javascript:void(0)" onclick="${loadFunction.name}(${i})">${i}</a>
            </li>
        `;
    }

    html += `
                <li class="page-item ${page === total_pages ? 'disabled' : ''}">
                    <a class="page-link" href="javascript:void(0)" onclick="${page < total_pages ? `${loadFunction.name}(${page + 1})` : ''}">
                        <i class="fa-solid fa-chevron-right"></i>
                    </a>
                </li>
            </ul>
        </nav>
    `;

    $container.html(html);
}

function exportOTExcel() {
    const month = $('#adminFilterMonth').val() || new Date().getMonth() + 1;
    const year = $('#adminFilterYear').val() || new Date().getFullYear();

    const downloadUrl = `${API_URL}/overtimes/export?month=${month}&year=${year}`;

    fetch(downloadUrl, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
    })
        .then(response => {
            if (response.status === 200) return response.blob();
            throw new Error('Không có quyền hoặc lỗi server');
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Bao_cao_OT_${month}_${year}.xlsx`;
            document.body.appendChild(a);
            a.click();
            a.remove();
        })
        .catch(error => displayToast(error.message, "danger"));
}