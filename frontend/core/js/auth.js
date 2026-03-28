// ===== CHECK LOGIN =====
function checkAuth() {
    const token = localStorage.getItem("token");

    if (!token) {
        // chưa login → đá về login
        window.location.href = "../../pages/Authentication/login.html";
    }
}

// ===== LOGOUT =====
function logout() {
    const confirmLogout = confirm("Bạn có chắc muốn đăng xuất không?");

    if (confirmLogout) {
        localStorage.removeItem("token");
        localStorage.removeItem("role");

        window.location.href = "../../pages/Authentication/login.html";
    }
}