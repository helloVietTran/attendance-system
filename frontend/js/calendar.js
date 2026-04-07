document.addEventListener('DOMContentLoaded', function () {
    // Lấy Role từ localStorage (Hoặc thay đổi logic theo thực tế dự án của bạn)
    const userRole = localStorage.getItem('role') || 'admin'; // Cấu hình 'admin' hoặc 'user' để test

    let calendarEl = document.getElementById('calendar');
    let calendar;
    let vacationsData = [];
    let makeupDaysData = [];
    let makeupDaysMap = {}; // Lưu map {date: id} để delete

    // Khởi tạo các Modal của Bootstrap
    const vacationModal = new bootstrap.Modal(document.getElementById('vacationModal'));
    const makeupModal = new bootstrap.Modal(document.getElementById('makeupModal'));

    // Hiển thị nút "Tạo ngày làm bù" nếu là Admin
    if (userRole === 'admin') {
        document.getElementById('btn-add-makeup').classList.remove('d-none');
    }

    // Cấu hình FullCalendar
    calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'vi', // Tiếng Việt
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth'
        },
        buttonText: {
            today: 'Hôm nay',
            month: 'Tháng'
        },
        height: 'auto',

        // Hook để xử lý màu nền (Trắng) cho ngày làm bù rơi vào Thứ 7, CN
        dayCellClassNames: function (arg) {
            const dateStr = arg.date.toISOString().split('T')[0];
            if (makeupDaysData.includes(dateStr)) {
                return ['is-makeup-day']; // Thêm class để CSS ghi đè thành màu trắng
            }
            return [];
        },

        // Xử lý sự kiện click vào ô lịch
        dateClick: function (info) {
            if (userRole !== 'admin') return; // Role thường chỉ được xem

            const clickedDate = info.dateStr;

            // Kiểm tra xem ngày này có phải ngày làm bù không
            if (makeupDaysMap[clickedDate]) {
                const compensation = makeupDaysMap[clickedDate];
                const message = compensation.description
                    ? `Lý do: ${compensation.description}\n\nXóa ngày làm bù này?`
                    : 'Xóa ngày làm bù này?';
                if (confirm(message)) {
                    deleteCompensation(compensation.id);
                }
                return;
            }

            // Kiểm tra xem ngày này đã có lịch nghỉ chưa
            const existingVacation = vacationsData.find(v => v.date === clickedDate);

            if (existingVacation) {
                // Nếu đã có -> Mở Modal ở chế độ Xóa
                openVacationModal(clickedDate, existingVacation);
            } else {
                // Nếu chưa có -> Mở Modal ở chế độ Thêm mới
                openVacationModal(clickedDate, null);
            }
        }
    });

    calendar.render();
    loadCalendarData();

    // ==========================================
    // CÁC HÀM XỬ LÝ DỮ LIỆU & GIAO DIỆN
    // ==========================================

    function loadCalendarData() {
        // Gộp 2 API lấy ngày nghỉ và ngày làm bù. Dùng Promise.all để chạy song song
        Promise.all([
            $.ajax({
                url: '/calendar/vacations',
                method: 'GET',
                dataType: 'json'
            }).catch(err => {
                console.error('Error loading vacations:', err);
                return { data: [] };
            }),
            $.ajax({
                url: '/calendar/compensations',
                method: 'GET',
                dataType: 'json'
            }).catch(err => {
                console.error('Error loading compensations:', err);
                return { data: [] };
            })
        ]).then(([vacationsRes, compensationsRes]) => {
            // Xử lý dữ liệu từ API response (API trả về { data: [...] })
            const vacationsRaw = vacationsRes?.data || [];
            const compensationsRaw = compensationsRes?.data || [];

            // Mapping loại ngày nghỉ sang CSS class
            const typeToClass = {
                'holiday': 'vacation-annual-bg',
                'emergency': 'vacation-emergency-bg',
                'event': 'vacation-company_event-bg'
            };

            // Convert vacation data: Từ {id, title, start_date, end_date, vacation_type, description} 
            // thành mảng {id, date, vacationType, title, description} cho từng ngày
            vacationsData = [];
            vacationsRaw.forEach(vacation => {
                const startDate = new Date(vacation.start_date);
                const endDate = new Date(vacation.end_date);

                // Lặp từ start_date đến end_date
                let currentDate = new Date(startDate);
                while (currentDate <= endDate) {
                    const dateStr = currentDate.toISOString().split('T')[0]; // yyyy-mm-dd format
                    vacationsData.push({
                        id: vacation.id,
                        date: dateStr,
                        vacationType: vacation.vacation_type,
                        title: vacation.title,
                        description: vacation.description,
                        cssClass: typeToClass[vacation.vacation_type] || 'vacation-annual-bg'
                    });
                    currentDate.setDate(currentDate.getDate() + 1);
                }
            });

            // Convert compensation data: Từ mảng {id, title, compensate_date, description}
            // thành mảy date strings và lưu map id + description
            makeupDaysData = compensationsRaw.map(comp => comp.compensate_date);
            makeupDaysMap = {};
            compensationsRaw.forEach(comp => {
                makeupDaysMap[comp.compensate_date] = {
                    id: comp.id,
                    description: comp.description
                };
            });

            renderEventsToCalendar();
        }).catch(err => {
            console.error('Error loading calendar data:', err);
        });
    }


    function renderEventsToCalendar() {
        calendar.removeAllEvents();

        // Thêm sự kiện ngày nghỉ (Sẽ tô màu full ô lịch)
        vacationsData.forEach(vacation => {
            // Event 1: Background color dựa trên loại ngày nghỉ
            calendar.addEvent({
                id: vacation.id,
                title: '',
                start: vacation.date,
                display: 'background',
                classNames: [vacation.cssClass],
                extendedProps: { type: vacation.vacationType }
            });

            // Event 2: Hiển thị text trên 2 dòng (title = loại, description = lý do)
            const displayText = vacation.title + (vacation.description ? ' - ' + vacation.description : '');
            calendar.addEvent({
                id: vacation.id + '_text',
                title: displayText,
                start: vacation.date,
                textColor: 'white',
                color: 'transparent',
                display: 'block'
            });
        });

        // Thêm text hiển thị cho ngày làm bù
        makeupDaysData.forEach(date => {
            const compensation = makeupDaysMap[date];

            // Event 1: Background color cho ngày làm bù
            calendar.addEvent({
                id: 'makeup_' + date,
                title: '',
                start: date,
                display: 'background',
                classNames: ['is-makeup-day']
            });

            // Event 2: hiển thị text "Làm bù" + lý do (1 dòng gọn)
            let displayText = 'Làm bù';
            if (compensation && compensation.description) {
                displayText += ' - ' + compensation.description;
            }

            calendar.addEvent({
                id: 'makeup_text_' + date,
                title: displayText,
                start: date,
                textColor: '#000',
                color: 'transparent',
                display: 'block',
                editable: false
            });
        });
    }

    function openVacationModal(date, existingData) {
        document.getElementById('vacationDate').value = date;
        document.getElementById('displayDate').value = date.split('-').reverse().join('/'); // Hiển thị DD/MM/YYYY

        if (existingData) {
            // Chế độ CẬP NHẬT/XÓA - Hiển thị thông tin đã lưu
            document.getElementById('vacationModalTitle').innerText = 'Chi tiết ngày nghỉ';
            document.getElementById('vacationId').value = existingData.id;

            // Mapping ngược: vacation_type (holiday, emergency, event) -> dropdown value (annual, emergency, company_event)
            const typeReverseMap = {
                'holiday': 'annual',
                'emergency': 'emergency',
                'event': 'company_event'
            };
            document.getElementById('vacationType').value = typeReverseMap[existingData.vacationType] || 'annual';
            document.getElementById('vacationNote').value = existingData.description || '';

            // Ẩn nút lưu, hiện nút update và xóa, enable form để edit
            document.getElementById('btn-save-vacation').classList.add('d-none');
            document.getElementById('btn-update-vacation').classList.remove('d-none');
            document.getElementById('btn-delete-vacation').classList.remove('d-none');
            document.getElementById('vacationType').disabled = false;
            document.getElementById('vacationNote').disabled = false;
        } else {
            // Chế độ THÊM MỚI
            document.getElementById('vacationModalTitle').innerText = 'Thêm ngày nghỉ lễ';
            document.getElementById('vacationId').value = '';
            document.getElementById('vacationType').value = 'annual';
            document.getElementById('vacationNote').value = '';

            // Hiện nút lưu, ẩn nút update và xóa, enable form
            document.getElementById('btn-save-vacation').classList.remove('d-none');
            document.getElementById('btn-update-vacation').classList.add('d-none');
            document.getElementById('btn-delete-vacation').classList.add('d-none');
            document.getElementById('vacationType').disabled = false;
            document.getElementById('vacationNote').disabled = false;
        }

        vacationModal.show();
    }

    // ==========================================
    // CÁC SỰ KIỆN NÚT BẤM POST / DELETE API
    // ==========================================

    // LƯU NGÀY NGHỈ
    document.getElementById('btn-save-vacation').addEventListener('click', function () {
        const date = document.getElementById('vacationDate').value;
        const type = document.getElementById('vacationType').value;
        const reason = document.getElementById('vacationNote').value;

        // Mapping: "annual" -> "holiday", "emergency" -> "emergency", "company_event" -> "event"
        const typeMapping = {
            annual: 'holiday',
            emergency: 'emergency',
            company_event: 'event'
        };

        // Mapping: Loại sang tên hiển thị
        const typeDisplayMap = {
            annual: 'Nghỉ thường niên',
            emergency: 'Nghỉ khẩn cấp',
            company_event: 'Sự kiện công ty'
        };

        if (!typeMapping[type]) {
            alert('Loại nghỉ không hợp lệ: ' + type);
            return;
        }

        if (!reason.trim()) {
            alert('Vui lòng nhập lý do nghỉ!');
            return;
        }

        const vacationType = typeMapping[type];
        const typeDisplay = typeDisplayMap[type];

        const payload = {
            title: typeDisplay,
            description: reason,
            start_date: date,
            end_date: date,
            vacation_type: vacationType,
            is_paid: true,
            is_recurring: true
        };

        $.ajax({
            url: '/calendar/vacations',
            method: 'POST',
            data: JSON.stringify(payload),
            contentType: "application/json",
            success: function (res) {
                alert('Thêm ngày nghỉ thành công!');
                vacationModal.hide();
                loadCalendarData();
            },
            error: function (err) {
                console.error("Lỗi:", err);
                alert('Có lỗi xảy ra khi thêm ngày nghỉ.');
            }
        });
    });

    // XÓA NGÀY NGHỈ
    document.getElementById('btn-delete-vacation').addEventListener('click', function () {
        if (!confirm('Bạn có chắc chắn muốn xóa ngày nghỉ này không?')) return;

        const id = document.getElementById('vacationId').value;

        $.ajax({
            url: `/calendar/vacations/${id}`,
            method: 'DELETE',
            success: function (res) {
                alert('Xóa ngày nghỉ thành công!');
                vacationModal.hide();
                loadCalendarData();
            },
            error: function (err) {
                console.error("Lỗi:", err);
                alert('Có lỗi xảy ra khi xóa.');
            }
        });
    });

    // CẬP NHẬT NGÀY NGHỈ
    document.getElementById('btn-update-vacation').addEventListener('click', function () {
        const id = document.getElementById('vacationId').value;
        const type = document.getElementById('vacationType').value;
        const reason = document.getElementById('vacationNote').value;

        // Mapping: "annual" -> "holiday", "emergency" -> "emergency", "company_event" -> "event"
        const typeMapping = {
            annual: 'holiday',
            emergency: 'emergency',
            company_event: 'event'
        };

        // Mapping: Loại sang tên hiển thị
        const typeDisplayMap = {
            annual: 'Nghỉ thường niên',
            emergency: 'Nghỉ khẩn cấp',
            company_event: 'Sự kiện công ty'
        };

        if (!typeMapping[type]) {
            alert('Loại nghỉ không hợp lệ: ' + type);
            return;
        }

        if (!reason.trim()) {
            alert('Vui lòng nhập lý do nghỉ!');
            return;
        }

        const vacationType = typeMapping[type];
        const typeDisplay = typeDisplayMap[type];

        const payload = {
            title: typeDisplay,
            description: reason,
            vacation_type: vacationType,
            is_paid: true,
            is_recurring: true
        };

        $.ajax({
            url: `/calendar/vacations/${id}`,
            method: 'PUT',
            data: JSON.stringify(payload),
            contentType: "application/json",
            success: function (res) {
                alert('Cập nhật ngày nghỉ thành công!');
                vacationModal.hide();
                loadCalendarData();
            },
            error: function (err) {
                console.error("Lỗi:", err);
                alert('Có lỗi xảy ra khi cập nhật ngày nghỉ.');
            }
        });
    });

    // LƯU NGÀY LÀM BÙ
    document.getElementById('btn-save-makeup').addEventListener('click', function () {
        const date = document.getElementById('makeupDate').value;
        const note = document.getElementById('makeupNote').value.trim();

        if (!date) {
            alert('Vui lòng chọn ngày!');
            return;
        }

        if (!note) {
            alert('Vui lòng nhập lý do làm bù!');
            return;
        }

        const payload = {
            title: 'Ngày làm bù',
            compensate_date: date,
            description: note
        };

        $.ajax({
            url: '/calendar/compensations',
            method: 'POST',
            data: JSON.stringify(payload),
            contentType: "application/json",
            success: function (res) {
                alert('Tạo ngày làm bù thành công!');
                makeupModal.hide();
                document.getElementById('makeupForm').reset();
                loadCalendarData();
            },
            error: function (err) {
                console.error("Lỗi:", err);
                alert('Có lỗi xảy ra khi thêm ngày làm bù.');
            }
        });
    });

    // HÀM XÓA NGÀY LÀM BÙ
    function deleteCompensation(compensationId) {
        $.ajax({
            url: `/calendar/compensations/${compensationId}`,
            method: 'DELETE',
            success: function (res) {
                alert('Xóa ngày làm bù thành công!');
                loadCalendarData();
            },
            error: function (err) {
                console.error("Lỗi:", err);
                alert('Có lỗi xảy ra khi xóa ngày làm bù.');
            }
        });
    }
});