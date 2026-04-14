$(document).ready(function () {
    checkAuthAndGetUser();
    initMonthFilter();
});

function initMonthFilter() {
    const select = $("#stat-month");

    const options = [
        { value: 1, label: "1 tháng gần nhất" },
        { value: 3, label: "3 tháng gần nhất" },
        { value: 6, label: "6 tháng gần nhất" },
        { value: 12, label: "12 tháng gần nhất" }
    ];

    options.forEach(opt => {
        select.append(`
            <option value="${opt.value}" ${opt.value === 1 ? 'selected' : ''}>
                ${opt.label}
            </option>
        `);
    });

    select.on("change", function () {
        loadDashboard($(this).val());
    });

    // load mặc định 1 tháng
    loadDashboard(1);
}

function loadDashboard(month) {
    $.ajax({
        url: `/statistics/dashboard`,
        type: "GET",
        data: { months: month },

        success: function (res) {
            if (res.status === 1000) {
                renderTopHard(res.data.top_hard_working);
                renderTopLate(res.data.top_late_leavers);
                renderChart(res.data.ratios);
            }
        },

        error: function () {
            showToast("Không tải được thống kê", "danger");
        }
    });
}

function renderTopHard(list) {
    const container = $("#top-hard-working");
    container.empty();

    let html = `
        <div class="table-responsive">
        <table class="table table-sm align-middle mb-0">
            <thead class="text-muted small">
                <tr>
                    <th>Tên</th>
                    <th>ID</th>
                    <th>Đi muộn/Về sớm</th>
                    <th>Số ngày nghỉ</th>
                </tr>
            </thead>
            <tbody>
    `;

    list.forEach((e, index) => {
        html += `
            <tr>
                <td class="fw-semibold">${e.full_name}</td>
                <td class="text-muted">${e.employee_id}</td>
                <td class="">${e.total_offence_minutes}p</td>
                <td class="">${e.total_absences}</td>
            </tr>
        `;
    });

    html += `</tbody></table></div>`;

    container.html(html);
}
function renderTopLate(list) {
    const container = $("#top-late");
    container.empty();

    let html = `
        <div class="table-responsive">
        <table class="table table-sm align-middle mb-0">
            <thead class="text-muted small">
                <tr>
                    <th>Tên</th>
                    <th>ID</th>
                    <th>Giờ về</th>
                    <th>Ngày</th>
                </tr>
            </thead>
            <tbody>
    `;

    list.slice(0, 5).forEach((e, index) => {
        html += `
            <tr>
                <td class="">${e.full_name}</td>
                <td class="text-muted">${e.employee_id}</td>
                <td class="fw-medium">${e.last_check_out}</td>
                <td class="text-muted">${formatDate(e.on_date)}</td>
            </tr>
        `;
    });

    html += `</tbody></table></div>`;

    container.html(html);
}
let chart;

function renderChart(data) {
    const ctx = document.getElementById("ratioChart");

    if (chart) chart.destroy();

    chart = new Chart(ctx, {
        type: "pie",
        data: {
            labels: ["Đúng giờ", "Muộn/Sớm", "Vắng"],
            datasets: [{
                data: [
                    data.on_time_percentage,
                    data.late_early_percentage,
                    data.absent_percentage
                ]
            }]
        },
        options: {
            plugins: {
                legend: {
                    position: "bottom"
                }
            }
        }
    });
}

function formatDate(dateStr) {
    const d = new Date(dateStr);
    return `${d.getDate()}/${d.getMonth() + 1}/${d.getFullYear()}`;
}