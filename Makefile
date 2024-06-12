
include .env
export

all: start-func serve

provision: 
	./scripts/provision.sh

start-func:
	cd src/function && poetry run func host start --port 7071

serve:
	cd src/api && poetry run uvicorn app:app --reload 

format:
	black . 
	isort . 