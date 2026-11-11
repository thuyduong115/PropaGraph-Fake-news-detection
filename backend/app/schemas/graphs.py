from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Feature = Literal["profile", "bert"]


class DatasetInfo(BaseModel):
    name: str
    n_graphs: int
    labels: list[str]


class GraphSummary(BaseModel):
    gid: int
    news_id: str | None
    title: str | None
    label: str | None
    n_nodes: int
    depth: int
    span_h: float | None
    growth: list[int] = Field(description="Số node nhìn thấy tại từng mốc của timeline_h")


class GraphPage(BaseModel):
    dataset: str
    total: int
    page: int
    size: int
    timeline_h: list[float | None]
    items: list[GraphSummary]


class Node(BaseModel):
    id: int
    depth: int
    t_rel_h: float | None


class GraphDetail(GraphSummary):
    dataset: str
    nodes: list[Node]
    edges: list[tuple[int, int]]


class TimelinePoint(BaseModel):
    cutoff_h: float | None
    n_nodes_used: int
    prob_fake: float | None


class Timeline(BaseModel):
    dataset: str
    gid: int
    feature: Feature
    model_ready: bool
    n_nodes_total: int
    points: list[TimelinePoint]


class PredictRequest(BaseModel):
    dataset: Literal["politifact", "gossipcop"]
    gid: int
    feature: Feature
    cutoff_h: float | None = Field(default=None, gt=0)


class PredictResponse(BaseModel):
    prob_fake: float
    pred_label: str
    n_nodes_used: int
    n_nodes_total: int
    model: str
