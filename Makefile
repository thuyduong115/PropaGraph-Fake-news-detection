# Dùng trên Linux / WSL / CI. Trên Windows không có make: python scripts/run.py <lệnh>
PY ?= python

.PHONY: setup dev web test lint format check docker

setup:
	$(PY) scripts/run.py setup

dev:
	$(PY) scripts/run.py dev

test:
	$(PY) scripts/run.py test

lint:
	$(PY) scripts/run.py lint

format:
	$(PY) scripts/run.py format

check:
	$(PY) scripts/check_artifacts.py

web:
	$(PY) scripts/run.py web

docker:
	docker compose up --build
