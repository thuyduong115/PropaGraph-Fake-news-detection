from __future__ import annotations

from pydantic import BaseModel


class TableInfo(BaseModel):
    name: str
    group: str
    n_rows: int


class TableData(TableInfo):
    columns: list[str]
    rows: list[list[str]]


class FigureInfo(BaseModel):
    name: str
    url: str
