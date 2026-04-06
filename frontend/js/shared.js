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

function updateHeaderUserInfo() {
    try {
        const userData = localStorage.getItem("user");
        if (!userData) return;

        const user = JSON.parse(userData);

        // 1. Hiển thị Email
        const emailElem = document.getElementById('user-email-display');
        if (emailElem && user.email) {
            emailElem.innerText = user.email;
        }

        // 2. Hiển thị Chữ cái đầu in hoa cho Badge
        const nameElem = document.getElementById('user-name-badge');
        if (nameElem && user.full_name) {
         
            const firstName = user.full_name.trim().split(' ').pop(); 
            const firstLetter = firstName.charAt(0).toUpperCase();
            
            nameElem.innerText = firstLetter;
        }
    } catch (error) {
        console.error("Không thể lấy thông tin user từ localStorage", error);
    }
}

updateHeaderUserInfo();