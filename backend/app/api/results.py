from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.api.deps import current_principal, get_registry
from app.core.registry import Registry
from app.schemas.results import FigureInfo, TableData, TableInfo

router = APIRouter(prefix="/results", tags=["results"], dependencies=[Depends(current_principal)])

RegistryDep = Annotated[Registry, Depends(get_registry)]


@router.get("/tables", response_model=list[TableInfo])
def list_tables(reg: RegistryDep, group: str | None = None) -> list[TableInfo]:
    return [
        TableInfo(name=t.name, group=t.group, n_rows=len(t.rows))
        for t in reg.tables.values()
        if group is None or t.group == group
    ]


@router.get("/tables/{name}", response_model=TableData)
def get_table(name: str, reg: RegistryDep) -> TableData:
    t = reg.tables.get(name)
    if t is None:
        raise HTTPException(status_code=404, detail=f"Không có bảng {name}")
    return TableData(name=t.name, group=t.group, n_rows=len(t.rows), columns=t.columns, rows=t.rows)


@router.get("/figures", response_model=list[FigureInfo])
def list_figures(reg: RegistryDep) -> list[FigureInfo]:
    return [FigureInfo(name=n, url=f"/api/results/figures/{n}") for n in reg.figures]


@router.get("/figures/{name}", response_class=FileResponse)
def get_figure(name: str, reg: RegistryDep) -> FileResponse:
    # chỉ trả file đã liệt kê lúc nạp: tên lạ hay "../" đều 404
    path = reg.figures.get(name)
    if path is None or not path.is_file():
        raise HTTPException(status_code=404, detail=f"Không có hình {name}")
    return FileResponse(path, media_type="image/png")
