$(document).ready(function () {
    checkAuthAndGetUser();
    const userRole = JSON.parse(localStorage.getItem("user"))?.role;

    const adminRoles = ["admin", "hr"];

    if (adminRoles.includes(userRole)) {
        const adminTab = document.getElementById("admin-ot-tab-item");
        if (adminTab) {
            adminTab.classList.remove("d-none");
        }
    }

    loadMyAbsenceRequests();

    $('button[data-bs-toggle="tab"]').on('shown.bs.tab', function (e) {
        const targetId = $(e.target).attr('data-bs-target');

        if (targetId === '#my-request') {
            // Nếu quay lại tab "Của tôi" -> Tải lại danh sách cá nhân
            loadMyAbsenceRequests();
        }
        else if (targetId === '#manage-request') {
            loadAdminAbsenceRequests(1);
        }
    });

    $('#addAbsenceForm').on('submit', function (e) {
        e.preventDefault();
        createAbsencePlan();
    });
});

/**
 * Call API tạo kế hoạch nghỉ phép mới
 */
function createAbsencePlan() {
    const absenceType = $('select[name="absence_type"]').val();
    const startDate = $('input[name="start_date"]').val();
    const endDate = $('input[name="end_date"]').val();
    const reason = $('textarea[name="reason"]').val().trim();

    if (new Date(endDate) < new Date(startDate)) {
        showToast("Ngày kết thúc không được trước ngày bắt đầu", "danger");
        return;
    }

    const payload = {
        absence_type: absenceType,
        start_date: startDate,
        end_date: endDate,
        reason: reason || null
    };

    $.ajax({
        url: `/absences/plans`,
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(payload),
        success: function (response) {
            showToast("Gửi yêu cầu nghỉ phép thành công!", "success");

            const modalElement = document.getElementById('addAbsenceModal');
            const modalInstance = bootstrap.Modal.getInstance(modalElement);
            modalInstance.hide();
            $('#addAbsenceForm')[0].reset();

        },
        error: function (xhr) {
            let errorMsg = "Lỗi khi gửi yêu cầu";
            if (xhr.responseJSON && xhr.responseJSON.detail) {
                errorMsg = typeof xhr.responseJSON.detail === 'string'
                    ? xhr.responseJSON.detail
                    : xhr.responseJSON.detail[0].msg;
            }
            showToast(errorMsg, "danger");
        }
    });
}

/**
 * Lấy danh sách kế hoạch nghỉ phép của cá nhân
 */
function loadMyAbsenceRequests() {
    const tbody = $('#absence-plans-body');

    $.ajax({
        url: `/absences/plans/me`,
        type: 'GET',
        success: function (response) {
            if (response.status === 1000 && Array.isArray(response.data)) {
                renderAbsenceTable(response.data);
            } else {
                tbody.html('<tr><td colspan="7" class="text-center">Chưa có kế hoạch nghỉ nào.</td></tr>');
            }
        },
        error: function () {
            tbody.html('<tr><td colspan="7" class="text-center text-danger">Lỗi tải dữ liệu nghỉ phép.</td></tr>');
        }
    });
}

/**
 * Render dữ liệu vào bảng
 */
function renderAbsenceTable(data) {
    const tbody = $('#absence-plans-body');

    if (!data || data.length === 0) {
        tbody.html('<tr><td colspan="7" class="empty-state-cell text-center">Bạn chưa có kế hoạch nghỉ nào.</td></tr>');
        return;
    }

    const rows = data.map(item => {
        const absenceTypeMap = {
            'annual': 'Nghỉ phép năm',
            'maternity': 'Nghỉ thai sản',
            'wedding': 'Nghỉ kết hôn',
            'funeral': 'Nghỉ tang chế',
            'paternity': 'Nghỉ vợ sinh'
        };
        const typeLabel = absenceTypeMap[item.absence_type] || item.absence_type;
        
        const statusBadge = getStatusBadge(item.status);
        const isPending = item.status.toUpperCase() === 'PENDING';

        const createdDate = new Date(item.created_at).toLocaleDateString('vi-VN');

        return `
            <tr>
                <td>${createdDate}</td>
                <td class="fw-bold text-primary">${item.start_date}</td>
                <td class="fw-bold text-primary">${item.end_date}</td>
                <td><span class="badge bg-light text-dark border">${typeLabel}</span></td>
                <td>
                    <div class="text-truncate" style="max-width: 200px;" title="${item.reason || ''}">
                        ${item.reason || '...'}
                    </div>
                </td>
                <td>${statusBadge}</td>
                <td class="text-center">
                    ${isPending ? 
                        `<button class="btn btn-sm btn-outline-danger" onclick="deleteAbsencePlan(${item.id})">
                            <i class="fa-solid fa-trash-can"></i>
                        </button>` : 
                        `<i class="fa-solid fa-lock text-muted" title="Đã xử lý"></i>`
                    }
                </td>
            </tr>
        `;
    }).join('');

    tbody.html(rows);
}

function getStatusBadge(status) {
    if (!status) return '<span class="badge bg-secondary">N/A</span>';
    status = status.toUpperCase();
    if (status === 'APPROVED') return '<span class="badge bg-success"><i class="fa-solid fa-check me-1"></i>Đã duyệt</span>';
    if (status === 'REJECTED') return '<span class="badge bg-danger"><i class="fa-solid fa-xmark me-1"></i>Từ chối</span>';
    return '<span class="badge bg-warning text-dark"><i class="fa-solid fa-clock me-1"></i>Chờ duyệt</span>';
}


function loadAdminAbsenceRequests(page = 1) {
    const status = $('#adminFilterStatus').val();
    const search = $('#adminSearchName').val();

    $.ajax({
        url: `/absences/plans/all`,
        type: 'GET',
        data: { 
            page: page, 
            limit: 10, 
            status: status,
            search: search ? search.trim() : undefined
        },
        success: function (response) {
            if (response.status === 1000) {
                renderAdminAbsenceTable(response.data);
                if (response.pagination) {
                    renderPagination(response.pagination, 'admin-absence-pagination', loadAdminAbsenceRequests);
                }
            }
        },
        error: function (xhr) {
            showToast("Lỗi khi tải danh sách quản lý", "danger");
        }
    });
}

/**
 * Render bảng quản lý cho Admin/HR
 */
function renderAdminAbsenceTable(data) {
    const tbody = $('#admin-absence-tbody');
    
    if (!data || data.length === 0) {
        tbody.html('<tr><td colspan="7" class="text-center py-4">Không có yêu cầu nào cần xử lý.</td></tr>');
        return;
    }

    const rows = data.map(item => {
        const isPending = item.status.toUpperCase() === 'PENDING';
        
        const typeMap = {
            'annual': 'Nghỉ phép năm',
            'wedding': 'Nghỉ kết hôn',
            'funeral': 'Nghỉ tang chế',
            'maternity': 'Nghỉ thai sản',
            'paternity': 'Nghỉ vợ sinh'
        };

        return `
            <tr>
                <td>
                    <div class="fw-bold">${item.employee_name || 'Nhân viên'}</div>
                    <small class="text-muted">ID: ${item.employee_id}</small>
                </td>
                <td><span class="badge bg-light text-dark border">${typeMap[item.absence_type] || item.absence_type}</span></td>
                <td><span class="text-primary fw-medium">${item.start_date}</span></td>
                <td><span class="text-primary fw-medium">${item.end_date}</span></td>
                <td>
                    <div class="text-truncate" style="max-width: 150px;" title="${item.reason || ''}">
                        ${item.reason || '...'}
                    </div>
                </td>
                <td>${getStatusBadge(item.status)}</td>
                <td class="text-center">
                    ${isPending ? `
                        <div class="btn-group">
                            <button class="btn btn-sm btn-success" onclick="updateAbsenceStatus(${item.id}, 'APPROVED')" title="Duyệt">
                                <i class="fa-solid fa-check"></i>
                            </button>
                            <button class="btn btn-sm btn-danger" onclick="updateAbsenceStatus(${item.id}, 'REJECTED')" title="Từ chối">
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

/**
 * Hàm gọi API Duyệt/Từ chối
 */
function updateAbsenceStatus(planId, newStatus) {
    const actionText = newStatus === 'APPROVED' ? "DUYỆT" : "TỪ CHỐI";
    if (!confirm(`Bạn có chắc chắn muốn ${actionText} yêu cầu này?`)) return;

    $.ajax({
        url: `/absences/plans/${planId}/status`,
        type: 'PATCH',
        contentType: 'application/json',
        data: JSON.stringify({ status: newStatus.toLowerCase() }),
        success: function () {
            showToast(`Đã ${actionText} yêu cầu`, "success");
            loadAdminAbsenceRequests(); // Tải lại bảng
        },
        error: function (xhr) {
            showToast("Lỗi cập nhật trạng thái", "danger");
        }
    });
}

/**
 * Xóa yêu cầu OT (chỉ khi đang PENDING)
 */
function deleteAbsencePlan(id) {
    if (!confirm("Bạn có chắc chắn muốn xóa yêu cầu này?")) return;

    $.ajax({
        url: `/absences/plans/${id}`,
        type: 'DELETE',
        success: function () {
            showToast("Đã xóa yêu cầu", "success");
            loadMyAbsenceRequests();
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