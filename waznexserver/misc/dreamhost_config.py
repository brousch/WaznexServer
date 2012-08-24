# -*- coding: utf-8 -*-
import os

# Configuration
DATA_FOLDER = '/home/barcampgr/talks.barcampgr.org/WaznexServer/data'
DEBUG = False
TESTING = False
HOST = '0.0.0.0'
SECRET_KEY = 'fdnsajflkdei573842ojrfje'
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATA_FOLDER + '/waznexserver.db'
SQLALCHEMY_ECHO = False
IMAGE_FOLDER = os.path.join(DATA_FOLDER, 'images')
DOWNSIZED_FOLDER = os.path.join(DATA_FOLDER, 'downsized')
THUMBNAIL_FOLDER = os.path.join(DATA_FOLDER, 'thumbnails')
ALLOWED_EXTENSIONS = set(['png',  'PNG',
                          'jpg',  'JPG',
                          'jpeg', 'JPEG',
                          'gif',  'GIF'])
FILE_NAME_DT_FORMAT = '%Y-%m-%dT%H:%M:%S'
PRETTY_DT_FORMAT = '%m/%d/%Y %I:%M:%S %p'
ENABLE_GRIDSPLITTER = True
GRIDSPLITTER_PYTHON = "/home/barcampgr/talks.barcampgr.org/WaznexServer/venv/bin/python"
GRIDSPLITTER_SLICER = "/home/barcampgr/talks.barcampgr.org/WaznexServer/gridsplitter/slice.py"
SPLIT_FOLDER = os.path.join(DATA_FOLDER, 'sliced')
GRIDSPLITTER_CELL_PREFIX = 'out-'
GRIDSPLITTER_COLOR = '2' # 'red', 'green' or 'blue'
GRIDSPLITTER_CELL_WIDTH = '320'
GRIDSPLITTER_CELL_HEIGHT = '207'
GRIDSPLITTER_MIN_COLS = 2
GRIDSPLITTER_MIN_ROWS = 2
GRIDSPLITTER_MAX_COLS = 8
GRIDSPLITTER_MAX_ROWS = 8
