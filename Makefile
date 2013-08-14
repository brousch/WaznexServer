.PHONY: clean_data
clean: clean_data_thumbnails clean_data_downsized clean_data_images clean_data_sliced clean_data_db

.PHONY: clean_all
clean_all: clean_venv clean_data

.PHONY: create_venv
create_venv:
	virtualenv -p python2.7 venv

.PHONY: clean_venv
clean_venv:
	rm -rf venv || true

.PHONY: clean_data_thumbnails
clean_data_thumbnails:
	rm -rf data/thumbnails/*.* || true

.PHONY: clean_data_downsized
clean_data_downsized:
	rm -rf data/downsized/*.* || true

.PHONY: clean_data_images
clean_data_images:
	rm -rf data/images/*.* || true

.PHONY: clean_data_sliced
clean_data_sliced:
	rm -rf data/sliced/* || true

.PHONY: clean_data_db
clean_data_db:
	rm data/*.sqlite || true

