dev:
	python3 -m uvicorn movies.main:app --reload --port=8001
install:
	poetry install