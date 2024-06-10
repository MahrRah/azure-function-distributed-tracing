
include .env

all: start-func serve

start-func:
	cd src/function && func host start --port 7071

serve:
	cd src/api && poetry run uvicorn app:app --reload 

format:
	black . 
	isort . 