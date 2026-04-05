async function checkAuth() {
    try {
        const res = await fetch(API_URL + "/auth/me", {
            method: "GET",
            credentials: "include" 
        });

        if (res.ok) {
            const data = await res.json();
            localStorage.setItem("user", JSON.stringify(data.data));

       
        } else {
            // Nếu trả về 401 hoặc 403 (Hết hạn session hoặc chưa login)
            console.warn("Session không hợp lệ, đang chuyển hướng...");
            redirectToLogin();
        }
    } catch (error) {
        console.error("Lỗi kết nối xác thực:", error);
        redirectToLogin();
    }
}

function redirectToLogin() {
    localStorage.clear();

    
}

checkAuth();