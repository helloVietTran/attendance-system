const BASE_URL = 'http://localhost:8000';
const API_PREFIX = '/api/v1';

const API_URL = BASE_URL + API_PREFIX;

// cấu hình ajax
$.ajaxPrefilter(function(options, originalOptions, jqXHR) {

    options.url = API_URL + options.url;

    const token = localStorage.getItem("access_token");
    if (token) {
        jqXHR.setRequestHeader('Authorization', `Bearer ${token}`);
    }
    

});

$(document).ajaxError(function(event, jqXHR, ajaxSettings, thrownError) {
    if (jqXHR.status === 401) {
        showToast("Phiên làm việc hết hạn, vui lòng đăng nhập lại", "danger");
    } else if(jqXHR.status === 403){
        showToast("Không có đủ quyền thực hiện hành động này", "danger");
    }else if (jqXHR.status === 500) {
        showToast("Lỗi hệ thống (500)", "danger");
    }
});
