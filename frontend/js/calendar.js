document.addEventListener('DOMContentLoaded', function () {
    checkAuthAndGetUser();

    const userRole = JSON.parse(localStorage.getItem('user'))?.role;
    const calendarEl = document.getElementById('calendar');
    const vModal = new bootstrap.Modal(document.getElementById('vacationModal'));
    const cModal = new bootstrap.Modal(document.getElementById('compensationModal'));
    const btnOpenVacation = document.getElementById('btn-open-vacation');
    const btnOpenComp = document.getElementById('btn-open-compensation');

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'vi',
        selectable: userRole === 'admin',
        unselectAuto: false,
        headerToolbar: { left: 'prev', center: 'title', right: 'next' },
        height: 'auto',

        select: function (info) {
            btnOpenVacation.disabled = false;
            btnOpenComp.disabled = false;
            prepareVacationData(info);
            prepareCompensationData(info);
        },

        unselect: function () {
            btnOpenVacation.disabled = true;
            btnOpenComp.disabled = true;
        },

        eventClick: function (info) {
            if (userRole !== 'admin') return;
            const ev = info.event;
            if (ev.extendedProps.isCompensation) {
                if (confirm(`Xóa ngày làm bù: ${ev.title}?`)) deleteCompensation(ev.id);
            } else {
                openVacationEditModal(ev);
            }
        },

        eventDataTransform: function (data) {
            const props = data.extendedProps;
            if (props.isCompensation) {
                data.backgroundColor = '#ffffff';
                data.borderColor = '#e2e8f0';
                data.textColor = '#262626';
            } else {
                data.backgroundColor = (props.vacation_type?.toLowerCase() === 'emergency') ? '#ffc107' : '#4caf50';
                data.borderColor = data.backgroundColor;
                data.textColor = '#ffffff';
            }
            return data;
        }
    });

    calendar.render();
    fetchEvents();

    function prepareVacationData(info) {
        document.getElementById('vacationForm').reset();
        document.getElementById('vacationId').value = '';
        document.getElementById('startDate').value = info.startStr;
        let endDate = new Date(info.end);
        endDate.setDate(endDate.getDate());
        document.getElementById('endDate').value = endDate.toISOString().split('T')[0];
        document.getElementById('btn-delete-vacation').classList.add('d-none');
    }

    function prepareCompensationData(info) {
        document.getElementById('compensationForm').reset();
        document.getElementById('compDate').value = info.startStr;
        document.getElementById('compTitle').value = "Làm bù";
    }

    btnOpenVacation.addEventListener('click', () => vModal.show());
    btnOpenComp.addEventListener('click', () => cModal.show());

    function openVacationEditModal(event) {
        prepareVacationData({
            startStr: event.startStr,
            end: event.end || new Date(new Date(event.startStr).getTime() + 86400000)
        });
        const props = event.extendedProps;
        document.getElementById('vacationId').value = event.id;
        document.getElementById('vacationTitle').value = event.title;
        document.getElementById('vacationDesc').value = props.description || '';
        document.getElementById('vacationType').value = props.vacation_type === 'EVENT' ? 'COMPANY_EVENT' : props.vacation_type;
        document.getElementById('btn-delete-vacation').classList.remove('d-none');
        vModal.show();
    }

    document.getElementById('btn-save-compensation').addEventListener('click', function () {
        const payload = {
            title: document.getElementById('compTitle').value || "Làm bù",
            compensate_date: document.getElementById('compDate').value,
            description: document.getElementById('compDesc').value || ""
        };
        $.ajax({
            url: '/calendar/compensations',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(payload),
            success: function () {
                cModal.hide();
                showToast("Đã tạo ngày làm bù", "success");
                calendar.unselect();
                fetchEvents();
            },
            error: handleAjaxError
        });
    });

    document.getElementById('btn-save-vacation').addEventListener('click', function () {
        const id = document.getElementById('vacationId').value;
        const type = document.getElementById('vacationType').value;
        const payload = {
            title: document.getElementById('vacationTitle').value || "Nghỉ lễ",
            description: document.getElementById('vacationDesc').value || "",
            start_date: document.getElementById('startDate').value,
            end_date: document.getElementById('endDate').value,
            vacation_type: type.toLowerCase() === 'company_event' ? 'event' : type.toLowerCase(),
            is_paid: true,
            is_recurring: type === 'HOLIDAY'
        };
        $.ajax({
            url: id ? `/calendar/vacations/${id}` : '/calendar/vacations',
            method: id ? 'PUT' : 'POST',
            contentType: 'application/json',
            data: JSON.stringify(payload),
            success: function () {
                vModal.hide();
                showToast(id ? "Cập nhật thành công" : "Tạo mới thành công", "success");
                calendar.unselect();
                fetchEvents();
            },
            error: handleAjaxError
        });
    });

    document.getElementById('btn-delete-vacation').addEventListener('click', function () {
        const id = document.getElementById('vacationId').value;
        if (confirm("Xóa dịp nghỉ này?")) {
            $.ajax({
                url: `/calendar/vacations/${id}`,
                method: 'DELETE',
                success: () => { vModal.hide(); fetchEvents(); },
                error: handleAjaxError
            });
        }
    });

    function fetchEvents() {
        calendar.removeAllEvents();
        Promise.all([
            $.ajax({ url: '/calendar/vacations?skip=0&limit=100' }),
            $.ajax({ url: '/calendar/compensations?skip=0&limit=100' })
        ]).then(([vRes, cRes]) => {
            const v = (vRes.data || []).map(i => ({
                id: i.id, title: i.title, start: i.start_date,
                end: addDays(i.end_date || i.start_date, 1),
                extendedProps: { vacation_type: i.vacation_type.toUpperCase(), description: i.description, isCompensation: false }
            }));
            const c = (cRes.data || []).map(i => ({
                id: 'comp_' + i.id, title: i.title, start: i.compensate_date,
                extendedProps: { isCompensation: true }
            }));
            calendar.addEventSource([...v, ...c]);
        });
    }

    function deleteCompensation(id) {
        $.ajax({
            url: `/calendar/compensations/${id.replace('comp_', '')}`,
            method: 'DELETE',
            success: () => { showToast("Đã xóa làm bù", "success"); fetchEvents(); },
            error: handleAjaxError
        });
    }

    function addDays(str, n) {
        const d = new Date(str); d.setDate(d.getDate() + n);
        return d.toISOString().split('T')[0];
    }
});

function handleAjaxError(xhr) {
    let message = "Có lỗi xảy ra";

    if (xhr.responseJSON?.message) {
        message = xhr.responseJSON.message;
    } else if (xhr.responseText) {
        message = xhr.responseText;
    }

    showToast(message, "danger");
}