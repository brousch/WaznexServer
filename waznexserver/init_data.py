#!/usr/bin/env python

import os
import traceback
import logging

import sqlalchemy.exc

from . import config
from . import models
from .models import db

log = logging.getLogger(__name__)

def create_data_dirs():
    data_folders = [df for df in dir(config) if df.endswith('_FOLDER')]
    for folder in data_folders:
        newdir = os.path.abspath(getattr(config, folder))
        print('Checking for, or creating', newdir)
        if not os.path.exists(newdir):  # If it doesn't exist, try to make it
            try:
                os.mkdir(newdir)
            except OSError:
                print("Unable to create data directory: " + newdir)
                traceback.print_exc()
                exit(1)
        if not os.path.exists(newdir):  # Make sure it's there now
            print("Unable to find or create data directory: " + newdir)
            exit(1)


def create_database():
    try:
        db.create_all()
    except sqlalchemy.exc.IntegrityError:
        log.info("Database tables already exist")
        db.session.rollback()
    else:
        db.session.commit()

    # Find and add all of the ImageStatuses in models.py
    statuses = [s for s in dir(models) if s.startswith('IMAGESTATUS_')]
    for status in statuses:
        id = getattr(models, status)
        s = models.ImageStatus(id, status.split('_', 1)[1])
        db.session.add(s)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            log.info("Status already exists in DB: " + status)
            db.session.rollback()

    # Find and add all of the ImageLevels in models.py
    levels = [l for l in dir(models) if l.startswith('IMAGELEVEL_')]
    for level in levels:
        id = getattr(models, level)
        l = models.ImageLevel(id, level.split('_', 1)[1])
        db.session.add(l)
        try:
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            log.info("Level already exists in DB: " + level)
            db.session.rollback()


if __name__ == '__main__':
    from .waznexserver import create_app

    create_data_dirs()

    app = create_app(initialize_data=False)
    with app.app_context():
        create_database()
