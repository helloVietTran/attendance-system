$(document).ready(function() { 
    updateHeaderUserInfo();
});

async function checkAuthAndGetUser() {
    const token = localStorage.getItem("access_token");
    
    if (!token) {
        redirectToLogin();
        return;
    }

    try {
        const res = await fetchWithAuth(API_URL + "/employees/me");

        if (!res.ok) {
            // Nếu token không hợp lệ (401) hoặc lỗi server
            throw new Error("Unauthorized or Session Expired");
        }

        const result = await res.json();

        localStorage.setItem("user", JSON.stringify(result.data));
    } catch (err) {
        console.error("Auth Error:", err);
    
        localStorage.removeItem("access_token");
        localStorage.removeItem("user");
        redirectToLogin();
    }
}

function redirectToLogin() {
    window.location.href = "./login.html"; 
}

async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem("access_token");
    return await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
            "Authorization": `Bearer ${token}`
        }
    });
}

function logout() { 
    localStorage.removeItem("user");
    localStorage.removeItem("access_token");
    window.location.href = "./login.html";
}

// lấy user từ localstorage tiêm vào header
function updateHeaderUserInfo() {
    const userStr = localStorage.getItem("user");
    if (userStr) {
        const user = JSON.parse(userStr);

        $('#user-email-display').text(user.email || 'N/A');
        
        const displayChar = user.full_name ? user.full_name.charAt(0) : (user.email ? user.email.charAt(0) : 'U');
        $('#user-name-badge').text(displayChar.toUpperCase());
    }
}

function showToast(message, type = 'success') {
    const $toastEl = $('#liveToast');
    
    $toastEl.removeClass('bg-success bg-danger');
    $toastEl.addClass(type === 'success' ? 'bg-success' : 'bg-danger');
    
    $('#toast-message').text(message);
    
    const toast = new bootstrap.Toast($toastEl[0]);
    toast.show();
}