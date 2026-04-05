/**
 * Các hàm tiện ích cho authentication
 */

const API_BASE_URL = "http://localhost:8000/api/v1";

/**
 * Kiểm tra xem user đã đăng nhập chưa
 */
function isLoggedIn() {
    return localStorage.getItem("token") !== null;
}

/**
 * Lấy token từ localStorage
 */
function getToken() {
    return localStorage.getItem("token");
}

/**
 * Lấy role từ localStorage
 */
function getRole() {
    return localStorage.getItem("role") || "user";
}

/**
 * Đăng xuất
 */
function logout() {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    window.location.href = "../pages/Authentication/login.html";
}

/**
 * Kiểm tra quyền admin
 */
function isAdmin() {
    return getRole() === "admin";
}

/**
 * Thực hiện login (dùng trong login.html)
 */
async function performLogin(email, password) {
    try {
        const res = await fetch(API_BASE_URL + "/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });

        const data = await res.json();

        if (res.status === 200) {
            localStorage.setItem("token", data.access_token);
            localStorage.setItem("role", data.role || "user");
            return { success: true };
        } else {
            return { success: false, message: data.detail || "Đăng nhập thất bại" };
        }

    } catch (e) {
        console.error(e);
        return { success: false, message: "Lỗi kết nối" };
    }
}

/**
 * Thực hiện register (dùng trong register.html)
 */
async function performRegister(username, email, password) {
    try {
        const res = await fetch(API_BASE_URL + "/auth/register", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ username, email, password })
        });

        const data = await res.json();

        if (res.status === 201 || res.status === 200) {
            return { success: true, message: "Đăng ký thành công!" };
        } else {
            return { success: false, message: data.detail || "Đăng ký thất bại" };
        }

    } catch (e) {
        console.error(e);
        return { success: false, message: "Lỗi kết nối" };
    }
}

/**
 * Tự động redirect nếu chưa đăng nhập
 */
function requireLogin() {
    if (!isLoggedIn()) {
        window.location.href = "../pages/Authentication/login.html";
    }
}

/**
 * Tự động redirect nếu không phải admin
 */
function requireAdmin() {
    if (!isLoggedIn()) {
        window.location.href = "../pages/Authentication/login.html";
    } else if (!isAdmin()) {
        alert("Bạn không có quyền truy cập trang này");
        window.location.href = "../pages/Dashboard/index.html";
    }
}