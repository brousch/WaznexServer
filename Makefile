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

# (re)builds the latest image and runs it
# the -q is necessary to get the container id, but then doesn't show build output
# so we add docker_build as a make target.  Its all cached anyway so fast.
.PHONY: docker_dev
docker_dev: docker_build
	docker run --rm -p 8080:8080 -it $(shell $(DOCKER_BUILD) -q)

# running with gunicorn (set in Dockerfile) won't use DEBUG mode, so this mode runs Flask's dev server
.PHONY: docker_dev_debug
docker_dev_debug: docker_build
	docker run --rm -p 8080:8080 -it $(shell $(DOCKER_BUILD) -q) python -m waznexserver.waznexserver


.PHONY: update_deps
update_deps:
	uv pip compile requirements.in -o requirements.txt
