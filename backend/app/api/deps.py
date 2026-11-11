from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request

from app.core.auth import ANONYMOUS, COOKIE_NAME, Authenticator, Principal
from app.core.registry import DATASETS, Registry


def get_registry(request: Request) -> Registry:
    return request.app.state.registry


def get_auth(request: Request) -> Authenticator:
    return request.app.state.auth


def current_principal(
    request: Request, auth: Annotated[Authenticator, Depends(get_auth)]
) -> Principal:
    principal = auth.read(request.cookies.get(COOKIE_NAME))
    if principal is not None:
        return principal
    if not auth.required:
        return ANONYMOUS
    raise HTTPException(status_code=401, detail="Cần đăng nhập")


def require_admin(principal: Annotated[Principal, Depends(current_principal)]) -> Principal:
    if principal.role != "admin":
        raise HTTPException(status_code=403, detail="Chỉ tài khoản admin được dùng chức năng này")
    return principal


def dataset_or_404(ds: str) -> str:
    if ds not in DATASETS:
        raise HTTPException(status_code=404, detail=f"Không có tập dữ liệu {ds}")
    return ds
