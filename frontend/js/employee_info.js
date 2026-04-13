$(document).ready(function () {
    loadEmployeeProfile();
    loadShifts();
    initHeatmapFilters();
    loadLeaveBalance();
});

function loadEmployeeProfile() {
    $.ajax({
        url: `/employees/me`,
        type: "GET",
        success: function (response) {
            if (response.status === 1000) {
                renderProfile(response.data);
            } else {
                showToast("Không thể lấy dữ liệu: " + response.message, "danger");
            }
        },
        error: function (xhr) {
            const errorMsg = xhr.responseJSON?.detail || "Lỗi kết nối máy chủ";
            showToast(errorMsg, "danger");
            // Nếu token hết hạn hoặc lỗi auth, chuyển về login
            if (xhr.status === 401) {
                window.location.href = "login.html";
            }
        },
    });
}

function renderProfile(data) {
    // 1. Thông tin cơ bản
    $("#info-full-name").text(data.full_name);
    $("#info-role").text(data.role.toUpperCase());
    $("#info-id").text(data.id);
    $("#info-email").text(data.email);
    $("#info-dept").text(data.department_id);
    $("#info-dob").text(data.dob || "Chưa cập nhật");

    // 2. Xử lý Avatar chữ cái đầu
    const initial = data.full_name.charAt(0).toUpperCase();
    $("#info-avatar-big").text(initial);

    // 3. Thông tin ca làm việc (Nested shift info)
    const shiftHtml = data.shift ? `
    <div class="d-flex justify-content-between align-items-center">
        <div>
            <div class="fw-semibold">${data.shift.name}</div>
            <small class="text-muted">
                ${data.shift.start_time.substring(0, 5)} - ${data.shift.end_time.substring(0, 5)}
            </small>
        </div>
       
    </div>
` : `
    <div class="text-muted small">Chưa có ca làm việc</div>
`;



    const $avatarImg = $("#info-avatar-img");
    const $avatarPlaceholder = $("#info-avatar-placeholder");

    // Kiểm tra nếu có dữ liệu ảnh từ API
    if (data.avatar_url && data.avatar_url !== "") {
        $avatarImg.attr("src", data.avatar_url);
        $avatarImg.removeClass("d-none");
        $avatarPlaceholder.addClass("d-none");

        // Xử lý trường hợp link ảnh lỗi (404)
        $avatarImg.on("error", function () {
            $(this).addClass("d-none");
            $avatarPlaceholder.removeClass("d-none");
            $avatarPlaceholder.text(data.full_name.charAt(0).toUpperCase());
        });
    } else {
        // Nếu không có ảnh, dùng avatar mặc định là chữ cái đầu của tên
        $avatarImg.addClass("d-none");
        $avatarPlaceholder.removeClass("d-none");

        const initial = data.full_name ? data.full_name.charAt(0).toUpperCase() : "U";
        $avatarPlaceholder.text(initial);
    }

    $("#current-shift").html(shiftHtml);
}

function initHeatmapFilters() {
    const now = new Date();
    const monthSelect = $('#heatmap-month');
    const yearSelect = $('#heatmap-year');

    for (let m = 1; m <= 12; m++) {
        monthSelect.append(`<option value="${m}" ${m === now.getMonth() + 1 ? 'selected' : ''}>Tháng ${m}</option>`);
    }

    for (let y = now.getFullYear() - 1; y <= now.getFullYear() + 1; y++) {
        yearSelect.append(`<option value="${y}" ${y === now.getFullYear() ? 'selected' : ''}>Năm ${y}</option>`);
    }

    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const empId = user.id;

    monthSelect.add(yearSelect).on('change', () => {
        loadAttendanceHeatmap(empId);
    });

    // 🔥 load lần đầu
    loadAttendanceHeatmap(empId);
}

function loadAttendanceHeatmap(employeeId) {
    const month = $('#heatmap-month').val();
    const year = $('#heatmap-year').val();

    if (!employeeId) return;

    $('#attendance-heatmap').html("Đang tải...");

    $.get(`/attendance/daily-reports/${employeeId}`, { month, year })
        .done(res => {
            if (res.status === 1000) {
                renderHeatmap(res.data, month, year);
            } else {
                showToast("Lỗi dữ liệu", "danger");
            }
        })
        .fail(() => {
            showToast("Không thể tải heatmap", "danger");
        });
}

function renderHeatmap(reports, month, year) {
    const container = $('#attendance-heatmap');
    container.empty();

    const reportMap = normalizeReports(reports);

    const daysInMonth = new Date(year, month, 0).getDate();

    for (let d = 1; d <= daysInMonth; d++) {
        const data = reportMap[d];

        let statusClass = 'status-none';
        let title = `Ngày ${d}/${month}: Nghỉ hoặc chưa đi làm`;

        if (data) {
            const lack = data.lack_minutes || 0;
            const work = data.work_time_minutes || 0;

            if (work > 0 && lack === 0) {
                statusClass = 'status-full'; // xanh lá
                title = `Ngày ${d}: Đi làm đầy đủ`;
            }
            else if (lack > 0) {
                statusClass = 'status-warning'; // vàng
                title = `Ngày ${d}: Thiếu ${lack} phút`;
            }
            else {
                statusClass = 'status-off'; // xám
                title = `Ngày ${d}: Không đi làm`;
            }
        }

        container.append(`
            <div class="heatmap-day ${statusClass}" 
                 data-bs-toggle="tooltip"
                 title="${title}">
                ${d}
            </div>
        `);
    }

    // Tooltip
    $('[data-bs-toggle="tooltip"]').tooltip();
}

function normalizeReports(reports) {
    const map = {};

    reports.forEach(r => {
        const day = new Date(r.work_date).getDate();

        // Nếu trùng ngày → lấy record tốt hơn
        if (!map[day] || r.work_time_minutes > map[day].work_time_minutes) {
            map[day] = r;
        }
    });

    return map;
}

function loadShifts() {
    $.ajax({
        url: "/shift/all",
        type: "GET",

        success: function (res) {
            if (res.status === 1000) {
                const select = $("#shift-select");

                // Xóa option cũ (trừ option đầu)
                select.find("option:not(:first)").remove();

                res.data.forEach(s => {
                    select.append(`
                        <option value="${s.id}">
                            ${s.name} (${s.start_time.substring(0, 5)} - ${s.end_time.substring(0, 5)})
                        </option>
                    `);
                });
            } else {
                showToast(res.message || "Lỗi dữ liệu", "danger");
            }
        },

        error: function (xhr) {
            const msg = xhr.responseJSON?.message || "Không tải được danh sách ca";
            showToast(msg, "danger");
        }
    });
}

$("#shift-select").on("change", function () {
    const val = $(this).val();
    $("#btn-change-shift").prop("disabled", !val);
});


$("#btn-change-shift").on("click", function () {
    const shiftId = $("#shift-select").val();

    if (!shiftId) return;

    const btn = $(this);
    btn.prop("disabled", true).text("Đang gửi...");

    $.ajax({
        url: "/shift/shift-change-request",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            shift_id: shiftId
        }),
        success: function (res) {
            if (res.status === 1000) {
                showToast("Đổi ca thành công, ca mới sẽ được áp dụng vào tháng tiếp theo", "success");

                // reload profile để cập nhật
                loadEmployeeProfile();
            } else {
                showToast(res.message, "danger");
            }
        },
        error: function () {
            showToast("Lỗi gửi yêu cầu", "danger");
        },
        complete: function () {
            btn.prop("disabled", false).html(`<i class="fa-solid fa-repeat me-1"></i> Đổi ca`);
        }
    });
});

function loadLeaveBalance() {
    const container = $("#leave-balance");

    $.ajax({
        url: `/absences/tracker`,
        type: "GET",

        success: function (res) {
            if (res.status === 1000) {
                renderLeaveBalance(res.data);
            } else {
                container.html("Không có dữ liệu");
            }
        },

        error: function () {
            container.html("Lỗi tải dữ liệu");
        }
    });
}

function renderLeaveBalance(data) {
    console.log(data)
    const html = `
        <div class="leave-item">
            <span>Tổng phép năm:</span>
            <strong>${data.total_remaining} ngày</strong>
        </div>

        <div class="leave-item">
            <span>Đã sử dụng:</span>
            <strong class="leave-used">${data.carried_over_used + data.current_year_used} ngày</strong>
        </div>

        <div class="leave-item">
            <span>Còn lại:</span>
            <strong class="leave-remaining">${data.total_remaining - data.carried_over_used - data.current_year_used} ngày</strong>
        </div>
    `;

    $("#leave-balance").html(html);
}