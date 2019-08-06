#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from flask_sqlalchemy import SQLAlchemy
from waznexserver import app
from waznexserver import db


# Image Levels (basic thumbnails, full grid)
IMAGELEVEL_NOTHING = -1
IMAGELEVEL_BASIC = 0
IMAGELEVEL_GRID = 1

class ImageLevel (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(16))
    
    def __init__(self, id, desc):
        self.id = id
        self.desc = desc
    
    def __repr__(self):
        return '<id:%d %s>' % (self.id, self.desc)


# Image Statuses
IMAGESTATUS_BAD = -1
IMAGESTATUS_NEW = 0
IMAGESTATUS_IN_WORK = 1
IMAGESTATUS_DONE = 2

class ImageStatus (db.Model):
    id = db.Column(db.Integer, primary_key=True)
    desc = db.Column(db.String(16))
    
    def __init__(self, id, desc):
        self.id = id
        self.desc = desc
    
    def __repr__(self):
        return '<id:%d %s>' % (self.id, self.desc)


class GridItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    upload_dt = db.Column(db.DateTime(), index=True)
    filename = db.Column(db.String(64), unique=True)
    status = db.Column(db.Integer, db.ForeignKey('image_status.id'))
    level = db.Column(db.Integer, db.ForeignKey('image_level.id'))

    def __init__(self, upload_dt, filename):
        self.upload_dt = upload_dt
        self.filename = filename
        self.status = IMAGESTATUS_NEW
        self.level = IMAGELEVEL_NOTHING
        
    def __repr__(self):
        return '<id:%d filename:%s status:%d level:%d>' % (self.id,
                                                             self.filename,
                                                            self.status,
                                                             self.level)
    
    def get_thumbnail_path(self):
        return os.path.join(app.config['THUMBNAIL_FOLDER'], self.filename)
    
    def get_downsized_path(self):
        return os.path.join(app.config['DOWNSIZED_FOLDER'], self.filename)
    
    def get_image_path(self):
        return os.path.join(app.config['IMAGE_FOLDER'], self.filename)
        
    def get_split_path(self):
        # Get the file name without extension
        fn_parts = self.filename.split('.')
        fn = ''.join(fn_parts[:-1])
        return os.path.join(app.config['SPLIT_FOLDER'], fn)
        
    def get_split_rel_path(self):
        fn_parts = self.filename.split('.')
        return fn_parts[-2]


class GridCell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fk_grid_item = db.Column(db.Integer, 
                             db.ForeignKey('grid_item.id'), 
                             index=True)
    grid_item = db.relationship("GridItem")
    filename = db.Column(db.String(16))
    col = db.Column(db.Integer)
    row = db.Column(db.Integer)
    
    def __init__(self, grid_item, filename, col, row):
        self.fk_grid_item = grid_item
        self.filename = filename
        self.col = col
        self.row = row
    
    def __repr__(self):
        return '<id:%d part_of:%d filename: %d>' % (self.id, 
                                                    self.grid_item,
                                                    self.filename)


class TweetFetchImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fetch_dt = db.Column(db.DateTime(), index=True)
    url = db.Column(db.String(254))
    
    def __init__(self, fetch_ts, url):
        self.fetch_dt = fetch_ts
        self.url = url
        
    def __repr__(self):
        return '<id:%d url:%s>' % (self.id, self.url)
        
