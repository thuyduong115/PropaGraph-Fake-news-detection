from __future__ import annotations

from fastapi import Request

from app.core.registry import Registry


def get_registry(request: Request) -> Registry:
    return request.app.state.registry
