from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import current_principal, dataset_or_404, get_registry
from app.core.registry import DATASETS, Registry
from app.schemas.graphs import (
    DatasetInfo,
    Feature,
    GraphDetail,
    GraphPage,
    GraphSummary,
    Timeline,
    TimelinePoint,
)
from app.services.inference import model_ready
from app.services.samples import TIMELINE, Graph, observed_count

router = APIRouter(tags=["graphs"], dependencies=[Depends(current_principal)])

RegistryDep = Annotated[Registry, Depends(get_registry)]


def _graph_or_404(reg: Registry, ds: str, gid: int) -> Graph:
    graph = reg.graphs.get(ds, {}).get(gid)
    if graph is None:
        raise HTTPException(status_code=404, detail=f"Không có đồ thị {gid} trong {ds}")
    return graph


@router.get("/datasets", response_model=list[DatasetInfo])
def datasets(reg: RegistryDep) -> list[DatasetInfo]:
    out = []
    for ds in DATASETS:
        graphs = reg.graphs.get(ds, {})
        labels = sorted({g.label for g in graphs.values() if g.label is not None})
        out.append(DatasetInfo(name=ds, n_graphs=len(graphs), labels=labels))
    return out


@router.get("/datasets/{ds}/graphs", response_model=GraphPage)
def list_graphs(
    reg: RegistryDep,
    ds: Annotated[str, Depends(dataset_or_404)],
    label: str | None = None,
    min_nodes: Annotated[int | None, Query(ge=0)] = None,
    max_nodes: Annotated[int | None, Query(ge=0)] = None,
    q: Annotated[str | None, Query(max_length=200)] = None,
    sort: Annotated[str, Query(pattern="^-?(gid|n_nodes|depth|span_h)$")] = "gid",
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=200)] = 20,
) -> GraphPage:
    items = list(reg.graphs.get(ds, {}).values())
    if label:
        items = [g for g in items if g.label == label]
    if min_nodes is not None:
        items = [g for g in items if g.n_nodes >= min_nodes]
    if max_nodes is not None:
        items = [g for g in items if g.n_nodes <= max_nodes]
    if q:
        needle = q.casefold()
        items = [g for g in items if g.title and needle in g.title.casefold()]

    key = sort.lstrip("-")
    items.sort(
        key=lambda g: (getattr(g, key) is None, getattr(g, key) or 0), reverse=sort.startswith("-")
    )
    start = (page - 1) * size
    return GraphPage(
        dataset=ds,
        total=len(items),
        page=page,
        size=size,
        timeline_h=list(TIMELINE),
        items=[GraphSummary(**g.summary()) for g in items[start : start + size]],
    )


@router.get("/datasets/{ds}/graphs/{gid}", response_model=GraphDetail)
def graph_detail(
    reg: RegistryDep, ds: Annotated[str, Depends(dataset_or_404)], gid: int
) -> GraphDetail:
    g = _graph_or_404(reg, ds, gid)
    return GraphDetail(dataset=ds, nodes=g.nodes, edges=g.edges, **g.summary())


@router.get("/datasets/{ds}/graphs/{gid}/timeline", response_model=Timeline)
def timeline(
    reg: RegistryDep,
    ds: Annotated[str, Depends(dataset_or_404)],
    gid: int,
    feature: Feature = "bert",
) -> Timeline:
    """Số node và xác suất tại mọi mốc trong một lần gọi. Chưa có model: `prob_fake = null`."""
    g = _graph_or_404(reg, ds, gid)
    ready = model_ready(reg, ds, feature)
    points = [
        TimelinePoint(cutoff_h=c, n_nodes_used=observed_count(g.nodes, c), prob_fake=None)
        for c in TIMELINE
    ]
    return Timeline(
        dataset=ds,
        gid=gid,
        feature=feature,
        model_ready=ready,
        n_nodes_total=g.n_nodes,
        points=points,
    )
