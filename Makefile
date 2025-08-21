BASE := /opt/waznexserver
VIRTUALENV := $(BASE)/env
BIN := $(VIRTUALENV)/bin
PYTHON := $(BIN)/python
PIP := $(BIN)/pip
PROJECT := $(BASE)/WaznexServer
DATA := $(PROJECT)/waznexserver/data

# from https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository
.PHONY: install_docker
install_docker:
	if ! command -v docker &> /dev/null; then \
		apt-get update && \
		apt-get install -y ca-certificates curl && \
		install -m 0755 -d /etc/apt/keyrings && \
		curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc && \
		chmod a+r /etc/apt/keyrings/docker.asc && \
		echo "deb [arch=$$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $$(. /etc/os-release && echo "$$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
		apt-get update && \
		apt-get install -y docker-ce docker-ce-cli containerd.io; \
	fi
	service docker start

.PHONY: init_production
init_production: install_docker docker_build
	apt install -y nginx
	cp -R $(PROJECT)/waznexserver/misc/systemd/etc/* /etc/
	systemctl daemon-reload
	mkdir $(DATA)

.PHONY: run_production
run_production: docker_prod
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


.PHONY: docker_prod
docker_prod:
	docker run -d --rm \
		-v $(DATA):$(DATA) \
		waznexserver

.PHONY: update_deps
update_deps:
	# python version should match what Dockerfile provides
	uv pip compile requirements.in -o requirements.txt --upgrade --python-version 3.12
