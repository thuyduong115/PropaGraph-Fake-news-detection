FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 \
    ARTIFACTS_DIR=/app/artifacts
WORKDIR /app

# torch + torch_geometric CPU, đúng phiên bản trong model_card.json (AGENTS.md quy tắc 4).
# Truyền khi build: --build-arg TORCH_VERSION=... --build-arg PYG_VERSION=...
# Để trống thì bỏ qua (image chỉ chạy được /api/health, /api/models).
ARG TORCH_VERSION=
ARG PYG_VERSION=
RUN if [ -n "$TORCH_VERSION" ]; then \
      pip install "torch==${TORCH_VERSION}" --index-url https://download.pytorch.org/whl/cpu && \
      pip install "torch_geometric==${PYG_VERSION}" ; fi

COPY pyproject.toml ./
COPY app ./app
RUN pip install .

RUN useradd --create-home --uid 1000 app
USER app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
