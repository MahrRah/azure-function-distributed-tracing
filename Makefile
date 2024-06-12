
include .env
export

all: start-func serve

provision: 
	./infra/provision.sh --create

deprovision: 
	./infra/setup.sh --delete

start-func:
	cd src/function && poetry run func host start --port 7071

serve:
	cd src/api && poetry run uvicorn app:app --reload 

format:
	black . 
	isort . 