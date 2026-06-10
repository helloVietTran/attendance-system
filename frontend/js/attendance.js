// Initialize the page when document is ready
$(document).ready(function () {
    checkAuthAndGetUser();
    checkFaceRegistrationPermission();
    loadAttendanceLogs();

    // Add enter key listener for search input
    $('#search-employee-input').on('keypress', function(e) {
        if (e.which === 13) { // Enter key
            searchEmployee();
        }
    });
});

/**
 * Check user role to determine if face registration button should be displayed
 * For now, always show the button as per user request
 */
function checkFaceRegistrationPermission() {
    // Always show the face registration button
    $('#btn-register-face').fadeIn().css('display', 'inline-block');
}

/**
 * Fetch attendance logs from the API for the current user and month
 */
function loadAttendanceLogs() {
    const userData = JSON.parse(localStorage.getItem("user") || "{}");
    const employeeId = userData.id;
    const attendanceTableBody = $('#attendance-log-tbody');

    if (!employeeId) {
        attendanceTableBody.html('<tr><td colspan="6" class="empty-state-cell text-danger">Không tìm thấy thông tin nhân viên</td></tr>');
        return;
    }

    // Display loading state
    attendanceTableBody.html('<tr><td colspan="6" class="empty-state-cell">Đang tải dữ liệu...</td></tr>');

    const currentDate = new Date();
    const day = currentDate.getDate();
    const month = currentDate.getMonth() + 1;
    const year = currentDate.getFullYear();

    $.ajax({
        url: `/attendance/logs/${employeeId}`,
        type: 'GET',
        data: {
            day: day,
            month: month,
            year: year
        },
        dataType: 'json',
        success: function (response) {
            console.log(response);
            if (response.status === 1000 && Array.isArray(response.data)) {
                displayAttendanceLogs(response.data);
            } else {
                attendanceTableBody.html('<tr><td colspan="6" class="empty-state-cell">Không có dữ liệu phù hợp.</td></tr>');
            }
        },
        error: function (xhr, status, error) {
            console.error("Lỗi lấy log chấm công:", error);
            attendanceTableBody.html('<tr><td colspan="6" class="empty-state-cell text-danger">Lỗi kết nối máy chủ hoặc API.</td></tr>');
        }
    });
}

/**
 * Render attendance logs into the table
 */
function displayAttendanceLogs(logs) {
    const attendanceTableBody = $('#attendance-log-tbody');

    if (!logs || !Array.isArray(logs) || logs.length === 0) {
        attendanceTableBody.html('<tr><td colspan="6" class="empty-state-cell">Chưa có dữ liệu chấm công.</td></tr>');
        return;
    }

    // Helper function to format time strings
    const formatTimeString = (timeStr) => {
        if (!timeStr) return "--:--";
        return timeStr.substring(0, 5);
    };

    // Generate HTML for table rows
    const tableRowsHtml = logs.map(logEntry => {
        return `
            <tr>
                <td>${logEntry.log_date}</td>
                <td>${formatTimeString(logEntry.shift_start)}</td>
                <td>${formatTimeString(logEntry.shift_end)}</td>
                <td class="text-primary fw-bold">${formatTimeString(logEntry.checked_time)}</td>
                <td>
                    <span class="badge bg-success-subtle text-success border border-success-subtle" style="font-size: 0.7rem;">
                        <i class="fa-solid fa-check-circle me-1"></i> Thành công
                    </span>
                </td>
            </tr>
        `;
    }).join('');

    attendanceTableBody.html(tableRowsHtml);
}

/**
 * Display a toast notification with the given message and type
 */
function displayToast(message, type = "success") {
    const toastElement = $('#liveToast');
    const toastMessage = $('#toast-message');

    // Remove existing background classes
    toastElement.removeClass('bg-success bg-danger bg-info');

    // Add appropriate background class based on type
    if (type === 'success') toastElement.addClass('bg-success');
    else if (type === 'danger') toastElement.addClass('bg-danger');
    else toastElement.addClass('bg-info');

    toastMessage.text(message);
    const toastInstance = new bootstrap.Toast(toastElement[0]);
    toastInstance.show();
}

// Global variable to hold the current video stream
let currentVideoStream = null;
// Variables for face registration
let selectedEmployeeId = null;
let selectedEmployeeName = null;
let capturedImages = [];
let isRegistering = false;
let autoCaptureInterval = null;

/**
 * Handle attendance check by opening camera modal and starting video stream
 */
async function startAttendanceCheck() {
    isRegistering = false;
    
    const cameraModalElement = document.getElementById('cameraModal');
    const cameraModalInstance = new bootstrap.Modal(cameraModalElement);

    // FIX: Chờ Modal hiển thị hoàn toàn rồi mới gọi camera
    cameraModalElement.addEventListener('shown.bs.modal', async function onModalShown() {
        const videoElement = document.getElementById('video');
        const loadingIndicator = document.getElementById('camera-loading');

        try {
            currentVideoStream = await navigator.mediaDevices.getUserMedia({
                video: { 
                    width: { ideal: 1280 }, 
                    height: { ideal: 720 } 
                },
                audio: false
            });
            videoElement.srcObject = currentVideoStream;
            loadingIndicator.style.display = 'none';
        } catch (err) {
            console.error("Không thể mở camera (Attendance):", err.name, err.message);
            displayToast("Không tìm thấy camera hoặc quyền truy cập bị từ chối!", "danger");
            cameraModalInstance.hide();
        }
    }, { once: true }); // Chạy duy nhất một lần cho đợt kích hoạt này

    cameraModalInstance.show();
}

/**
 * Stop the current video stream and release camera resources
 */
function stopVideoStream() {
    if (currentVideoStream) {
        currentVideoStream.getTracks().forEach(track => track.stop());
        currentVideoStream = null;
    }
}

/**
 * Capture image from video stream and send to face authentication API
 */
function captureAndSendImage() {
    const videoElement = document.getElementById('video');
    const canvas = document.getElementById('canvas');
    const snapButton = document.getElementById('snap');

    // Set canvas dimensions to match video
    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    const canvasContext = canvas.getContext('2d');
    canvasContext.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

    // Convert canvas to Blob
    canvas.toBlob(function(blob) {
        if (!blob) return;

        const imageFormData = new FormData();
        imageFormData.append('file', blob, 'attendance_face.png');

        const originalButtonText = snapButton.innerHTML;
        $(snapButton).prop('disabled', true)
                    .html(`<span class="spinner-border spinner-border-sm me-2"></span> Đang xác thực...`);

        $.ajax({
            url: `/face-auth/attendance`,
            type: 'POST',
            data: imageFormData,
            processData: false,
            contentType: false,
            success: function(result) {
                displayToast("Xác thực thành công! Đã ghi nhận log.", "success");

                // Close modal and stop camera
                const cameraModalElement = document.getElementById('cameraModal');
                const cameraModalInstance = bootstrap.Modal.getInstance(cameraModalElement);
                cameraModalInstance.hide();
                stopVideoStream();

                // Reload attendance logs
                loadAttendanceLogs();
            },
            error: function(xhr) {
                let errorMessage = "Xác thực thất bại!";
                if (xhr.responseJSON && xhr.responseJSON.detail) {
                    errorMessage = xhr.responseJSON.detail;
                }
                displayToast(errorMessage, "danger");
            },
            complete: function() {
                $(snapButton).prop('disabled', false).html(originalButtonText);
            }
        });
    }, 'image/png');
}

// ================== Face Registration Functions ==================

/**
 * Open the face registration modal
 */
function openRegisterFaceModal() {
    selectedEmployeeId = null;
    selectedEmployeeName = null;
    capturedImages = [];
    $('#search-employee-input').val('');
    $('#search-results').empty();
    $('#selected-employee-info').addClass('d-none');
    $('#btn-start-capture').prop('disabled', true);
    const registerModal = new bootstrap.Modal(document.getElementById('registerFaceModal'));
    registerModal.show();
}

/**
 * Search for employees using the API
 */
function searchEmployee() {
    const keyword = $('#search-employee-input').val().trim();
    if (!keyword) {
        displayToast("Vui lòng nhập từ khóa tìm kiếm", "info");
        return;
    }

    $('#search-results').html('<div class="text-center"><div class="spinner-border spinner-border-sm"></div> Đang tìm kiếm...</div>');

    $.ajax({
        url: '/employees/search',
        type: 'GET',
        data: { keyword: keyword, limit: 10 },
        dataType: 'json',
        success: function(response) {
            if (response.status === 1000 && Array.isArray(response.data)) {
                displaySearchResults(response.data);
            } else {
                $('#search-results').html('<div class="text-muted">Không tìm thấy nhân viên nào.</div>');
            }
        },
        error: function(xhr) {
            console.error("Lỗi tìm kiếm nhân viên:", xhr);
            $('#search-results').html('<div class="text-danger">Lỗi kết nối máy chủ.</div>');
        }
    });
}

/**
 * Display search results in the list
 */
function displaySearchResults(employees) {
    const resultsHtml = employees.map(emp => `
        <a href="#" class="list-group-item list-group-item-action" onclick="selectEmployee(${emp.id}, '${emp.full_name}')">
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <strong>${emp.full_name}</strong>
                    <br><small class="text-muted">ID: ${emp.id} | Email: ${emp.email}</small>
                </div>
                <i class="fa-solid fa-chevron-right text-muted"></i>
            </div>
        </a>
    `).join('');

    $('#search-results').html(resultsHtml || '<div class="text-muted">Không tìm thấy nhân viên nào.</div>');
}

/**
 * Select an employee from search results
 */
function selectEmployee(employeeId, fullName) {
    selectedEmployeeId = employeeId;
    selectedEmployeeName = fullName;
    $('#selected-emp-name').text(fullName);
    $('#selected-emp-id').text(employeeId);
    $('#selected-employee-info').removeClass('d-none');
    $('#btn-start-capture').prop('disabled', false);
    displayToast(`Đã chọn nhân viên: ${fullName}`, "success");
}

/**
 * Open camera for face registration after selecting employee
 */
function openCameraForRegister() {
    if (!selectedEmployeeId) {
        displayToast("Vui lòng chọn nhân viên trước", "warning");
        return;
    }

    // Close register modal
    const registerModalElement = document.getElementById('registerFaceModal');
    const registerModal = bootstrap.Modal.getInstance(registerModalElement);
    if (registerModal) registerModal.hide();

    // Open camera modal for registration
    isRegistering = true;
    capturedImages = [];
    
    // Đợi modal cũ ẩn hẳn để tránh chồng chéo backdrop (phụ của Bootstrap)
    setTimeout(() => {
        startRegistrationCamera();
    }, 400);
}

/**
 * Start camera for face registration
 */
async function startRegistrationCamera() {
    const cameraModalElement = document.getElementById('cameraModal');
    const cameraModalInstance = new bootstrap.Modal(cameraModalElement);

    // Change modal title and button text for registration trước khi show
    $('.modal-title').text('Đăng ký khuôn mặt - ' + selectedEmployeeName);
    $('#snap').hide(); 

    // FIX: Chờ Modal hiển thị hoàn toàn rồi mới gọi camera đăng ký
    cameraModalElement.addEventListener('shown.bs.modal', async function onRegisterModalShown() {
        const videoElement = document.getElementById('video');
        const loadingIndicator = document.getElementById('camera-loading');

        try {
            currentVideoStream = await navigator.mediaDevices.getUserMedia({
                video: { 
                    width: { ideal: 1280 }, 
                    height: { ideal: 720 } 
                },
                audio: false
            });
            videoElement.srcObject = currentVideoStream;
            loadingIndicator.style.display = 'none';

            // Add instruction text
            $('#cameraModal .modal-body p').text(`Đang tự động chụp 20 ảnh mẫu cho ${selectedEmployeeName}. Ảnh đã chụp: 0/20`);

            // Start automatic capture
            startAutoCapture();
        } catch (err) {
            console.error("Không thể mở camera (Register):", err.name, err.message);
            displayToast("Không tìm thấy camera hoặc quyền truy cập bị từ chối!", "danger");
            cameraModalInstance.hide();
        }
    }, { once: true });

    cameraModalInstance.show();
}

/**
 * Start automatic image capture every 100ms
 */
function startAutoCapture() {
    // Xóa interval cũ nếu lỡ còn tồn tại
    if (autoCaptureInterval) clearInterval(autoCaptureInterval);
    
    autoCaptureInterval = setInterval(() => {
        captureSampleImage();
    }, 100);
}

/**
 * Capture a sample image for face registration
 */
function captureSampleImage() {
    const videoElement = document.getElementById('video');
    const canvas = document.getElementById('canvas');

    if (!videoElement || !videoElement.videoWidth) return; // Đề phòng lỗi luồng chưa sẵn sàng từng mili-giây đầu

    canvas.width = videoElement.videoWidth;
    canvas.height = videoElement.videoHeight;
    const canvasContext = canvas.getContext('2d');
    canvasContext.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

    canvas.toBlob(function(blob) {
        if (blob) {
            capturedImages.push(blob);
            const count = capturedImages.length;
            $('#cameraModal .modal-body p').text(`Đang tự động chụp 20 ảnh mẫu cho ${selectedEmployeeName}. Ảnh đã chụp: ${count}/20`);

            if (count >= 20) {
                clearInterval(autoCaptureInterval);
                autoCaptureInterval = null;
                sendRegistration();
            }
        }
    }, 'image/png');
}

/**
 * Send captured images to server for face registration
 */
function sendRegistration() {
    if (capturedImages.length < 20) {
        displayToast("Cần chụp đủ 20 ảnh mẫu", "warning");
        return;
    }

    // Update UI to show processing
    $('#cameraModal .modal-body p').text(`Đang xử lý 20 ảnh mẫu cho ${selectedEmployeeName}...`);

    const formData = new FormData();
    capturedImages.forEach((blob, index) => {
        formData.append('files', blob, `sample_${index + 1}.png`);
    });

    $.ajax({
        url: `/face-auth/register/${selectedEmployeeId}`,
        type: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            displayToast(response.message || "Đăng ký khuôn mặt thành công!", "success");

            // Close modal and reset
            const cameraModalElement = document.getElementById('cameraModal');
            const cameraModalInstance = bootstrap.Modal.getInstance(cameraModalElement);
            if (cameraModalInstance) cameraModalInstance.hide();
            stopVideoStream();
            isRegistering = false;
        },
        error: function(xhr) {
            let errorMessage = "Đăng ký thất bại!";
            if (xhr.responseJSON && xhr.responseJSON.detail) {
                errorMessage = xhr.responseJSON.detail;
            }
            displayToast(errorMessage, "danger");
        }
    });
}

// Stop camera when modal is closed
document.getElementById('cameraModal').addEventListener('hidden.bs.modal', function() {
    stopVideoStream();
    if (autoCaptureInterval) {
        clearInterval(autoCaptureInterval);
        autoCaptureInterval = null;
    }
    isRegistering = false;
    // Reset modal title and button
    $('.modal-title').text('Xác thực khuôn mặt');
    $('#snap').show().html('<i class="fa-solid fa-circle-dot me-2"></i>Chụp ảnh & Điểm danh').attr('onclick', 'captureAndSendImage()');
    $('#cameraModal .modal-body p').text('Vui lòng nhìn thẳng vào camera và giữ yên.');
});