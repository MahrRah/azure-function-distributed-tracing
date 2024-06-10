
all: start

start:
	cd src/function && func start

run:
	cd src/api && poetry run uvicorn app:app --reload 

format:
	black . 
	isort . 