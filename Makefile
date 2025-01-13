BASE := /opt/waznexserver
VIRTUALENV := $(BASE)/env
BIN := $(VIRTUALENV)/bin
PYTHON := $(BIN)/python
PIP := $(BIN)/pip
PROJECT := $(BASE)/WaznexServer


.PHONY: init_production
init_production:
	sudo cp -R $(PROJECT)/waznexserver/misc/systemd/etc/* /etc/
	sudo systemctl daemon-reload

.PHONY: run_production
run_production:
	sudo service waznexserver restart
	sudo service waznex-process-grid restart
	sudo service nginx restart

DOCKER_BUILD := docker build -t waznexserver .

.PHONY: docker_build
docker_build:
	$(DOCKER_BUILD)

.PHONY: docker_dev
docker_dev:
	# (re)builds the latest image and runs it
	docker run --rm -p 8080:8080 -it $(shell $(DOCKER_BUILD) -q)

.PHONY: docker_dev_process
docker_dev_process:
	# connects to existing docker_dev and runs the processing script
	docker exec -it $(shell docker ps -q --filter ancestor=waznexserver) python -m waznexserver.process_grid

.PHONY: update_deps
update_deps:
	uv pip compile requirements.in -o requirements.txt
