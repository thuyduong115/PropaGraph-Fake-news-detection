from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response

from app.api.deps import current_principal, get_auth
from app.core.auth import COOKIE_NAME, Authenticator, Principal
from app.schemas.auth import LoginRequest, Me

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Me)
def login(
    body: LoginRequest,
    request: Request,
    response: Response,
    auth: Annotated[Authenticator, Depends(get_auth)],
) -> Me:
    principal = auth.verify(body.username, body.password)
    if principal is None:
        raise HTTPException(status_code=401, detail="Sai tên đăng nhập hoặc mật khẩu")
    response.set_cookie(
        COOKIE_NAME,
        auth.issue(principal),
        max_age=auth.session_seconds,
        httponly=True,
        samesite="lax",
        secure=request.app.state.settings.cookie_secure,
        path="/",
    )
    return Me(username=principal.username, role=principal.role, auth_required=auth.required)


@router.post("/logout", status_code=204)
def logout(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/")


@router.get("/me", response_model=Me)
def me(
    principal: Annotated[Principal, Depends(current_principal)],
    auth: Annotated[Authenticator, Depends(get_auth)],
) -> Me:
    return Me(username=principal.username, role=principal.role, auth_required=auth.required)
