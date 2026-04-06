async function login() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    if (!email || !password) {
        document.getElementById("message").innerText = "Vui lòng nhập email và mật khẩu";
        return;
    }

    try {
        const res = await fetch(API_URL + "/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email, password })
        });

        const result = await res.json();

        if (res.ok) {
            localStorage.setItem("access_token", result.data.access_token);

            window.location.href = "../../core/layout/base.html";
        } else {
            document.getElementById("message").innerText =
                result.detail || "Đăng nhập thất bại";
        }

    } catch (e) {
        console.error(e);
        document.getElementById("message").innerText =
            "Kiểm tra lại tài khoản và mật khẩu";
    }
}

document.getElementById("btnLogin").addEventListener("click", login);