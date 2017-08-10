BASE := /opt/waznexserver
VIRTUALENV := $(BASE)/env
BIN := $(VIRTUALENV)/bin
PYTHON := $(BIN)/python
PIP := $(BIN)/pip
PROJECT := $(BASE)/WaznexServer


.PHONY: clean_data
clean_data: clean_data_thumbnails clean_data_downsized clean_data_images clean_data_sliced clean_data_db

.PHONY: clean_all
clean_all: clean_venv clean_data

.PHONY: install_system_requirements
install_system_requirements:
	sudo apt-get update
	sudo apt-get install -y nginx python-dev libjpeg62 libjpeg-dev libfreetype6 libfreetype6-dev libtiff5 libtiff5-dev libwebp5 libwebp-dev zlib1g-dev

.PHONY: bootstrap_modern_python_tools
bootstrap_modern_python_tools:
	sudo apt-get remove --purge -y python-virtualenv python-pip python-setuptools
	wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python2.7
	sudo rm -f setuptools*.zip
	sudo easy_install-2.7 -U pip
	sudo pip2.7 install -U virtualenv

.PHONY: create_venv
create_venv:
	virtualenv -p python2.7 $(VIRTUALENV)
	$(PIP) install -r requirements.txt

.PHONY: init_data
init_data:
	$(PYTHON) waznexserver/utils.py

.PHONY: init_production
init_production:
	sudo cp -R $(PROJECT)/waznexserver/misc/systemd/etc/* /etc/

.PHONY: clean_venv
clean_venv:
	rm -rf ../env || true

.PHONY: clean_data_thumbnails
clean_data_thumbnails:
	rm -rf waznexserver/data/thumbnails/*.* || true

.PHONY: clean_data_downsized
clean_data_downsized:
	rm -rf waznexserver/data/downsized/*.* || true

.PHONY: clean_data_images
clean_data_images:
	rm -rf waznexserver/data/images/*.* || true

.PHONY: clean_data_sliced
clean_data_sliced:
	rm -rf waznexserver/data/sliced/* || true

.PHONY: clean_data_db
clean_data_db:
	rm waznexserver/data/*.db || true

.PHONY: run
run:
	$(PYTHON) waznexserver/waznexserver.py

.PHONY: run_production
run_production:
	sudo service waznexserver restart
	sudo service nginx restart
