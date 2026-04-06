const BASE_URL = 'http://localhost:8000';
const API_PREFIX = '/api/v1';

const API_URL = BASE_URL + API_PREFIX;

async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem("access_token");

    const res = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
            "Authorization": `Bearer ${token}`
        }
    });

    return res;
}

async function checkAuth() {
    try {
        const res = await fetchWithAuth(API_URL + "/auth/introspect");

        if (!res.ok) throw new Error();

        const data = await res.json();
        return data.data.authenticated;

    } catch (err) {
        console.log(err);
        return false;
    }
}

async function protectPage() {
    const isAuth = await checkAuth();

    if (!isAuth) {
        console.log("User not authenticated, redirecting to login...");
        //window.location.href = "../../pages/Authentication/login.html";
    }
}