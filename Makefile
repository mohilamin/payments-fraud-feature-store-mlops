.PHONY: install generate-data run-pipeline train-model score-batch monitor test lint format dashboard api docker-up docker-down

install:
	python -m pip install -r requirements.txt

generate-data:
	python -m src.data_generation.generate_synthetic_payments

run-pipeline:
	python -m src.pipeline.run_all

train-model:
	python -m src.training.train_model

score-batch:
	python -m src.scoring.score_batch

monitor:
	python -m src.monitoring.monitor

test:
	python -m pytest

lint:
	python -m ruff check .

format:
	python -m ruff format .

dashboard:
	python -m streamlit run src/dashboard/app.py

api:
	python -m uvicorn src.api.main:app --reload

docker-up:
	docker compose up --build

docker-down:
	docker compose down
