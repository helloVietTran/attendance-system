from fastapi import Depends, HTTPException, Request

def get_current_user(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Vui lòng đăng nhập")
    return {"id": user_id, "role": request.session.get("role")}

def role_required(allowed_roles: list):
    def decorator(current_user: dict = Depends(get_current_user)):
        if current_user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Bạn không có quyền thực hiện hành động này"
            )
        return current_user
    return decorator