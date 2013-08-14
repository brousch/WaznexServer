#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2011 Ben Rousch <brousch@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public 
#    License along with this program.  If not, see 
#    <http://www.gnu.org/licenses/>.


import os
#import time
import datetime
import config
from flask import Flask
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
#from flask import session
from flask import url_for
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from sqlalchemy import or_
from werkzeug import secure_filename

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_object(config)
app.config.from_envvar('WAZNEXSERVER_SETTINGS', silent=True)

db = SQLAlchemy(app)
import models
        
              
@app.route('/')
def index():
    # Fetch newest images from DB
    grid = db.session.query(models.GridItem).\
           filter_by(status=models.IMAGESTATUS_DONE).\
           order_by(desc('upload_dt')).\
           first()
    app.logger.info(grid)
    if grid is not None and \
       grid.level == models.IMAGELEVEL_GRID:
        cell_list = db.session.query(models.GridCell).\
                    filter_by(fk_grid_item=grid.id).\
                    order_by('row').order_by('col').all()
        app.logger.info('Found some cells: ' + str(len(cell_list)))
        grid.cells = cell_list
        # Set image width to fit a row without wrapping
        # Use last cell to get the number of columns 
        grid.cell_width = int(316/(cell_list[-1].col + 1))
    return render_template('index.html',
                           grid=grid,
                           pretty_dt_format=app.config['PRETTY_DT_FORMAT'])

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico',
                               mimetype='image/vnd.microsoft.icon')

@app.route('/thumbnail/<filename>')
def show_thumbnail(filename):
    app.logger.info('Serving thumbnail through Flask: ' + filename)
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename)

@app.route('/medium/<filename>')
def show_downsized(filename):
    app.logger.info('Serving downsized image through Flask: ' + filename)
    return send_from_directory(app.config['DOWNSIZED_FOLDER'], filename)

@app.route('/image/<filename>')
def show_image(filename):
    app.logger.info('Serving image through Flask: ' + filename)
    return send_from_directory(app.config['IMAGE_FOLDER'], filename)

@app.route('/diagnostic/<int:grid_item_id>')
def show_diagnostic(grid_item_id):
    grid_item = db.session.query(models.GridItem).\
                filter_by(id=grid_item_id).first()
    gsp = grid_item.get_split_path()
    filename = "lines.png"
    app.logger.info('Serving diagnostic image through Flask: ' + filename)
    return send_from_directory(os.path.join(app.config['SPLIT_FOLDER'], gsp),
                                            filename)

@app.route('/sliced/<int:grid_item_id>/<filename>')
def show_sliced(grid_item_id, filename):
    grid_item = db.session.query(models.GridItem).\
                filter_by(id=grid_item_id).first()
    gsp = grid_item.get_split_path()
    app.logger.info('Serving cell through Flask: ' + gsp + '/' + filename)
    return send_from_directory(os.path.join(app.config['SPLIT_FOLDER'], gsp),
                                            filename)
                                            
@app.route('/colview/<int:grid_item_id>/<int:col_num>')
def show_colview(grid_item_id, col_num):
    # Get column 0 - Room List
    # Get column col_num
    cells = db.session.query(models.GridCell).\
                filter_by(fk_grid_item=grid_item_id).\
                filter(or_(models.GridCell.col==0,
                           models.GridCell.col==col_num)).\
                order_by('row').order_by('col').all()
    cell_width = int(316/2)
    return render_template('colview.html', 
                           cell_list=cells,
                           cell_width=cell_width)

@app.route('/upload/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        if f and allowed_file(f.filename):
            # Name and save file to IMAGE folder
            upload_ts = datetime.datetime.utcnow() - datetime.timedelta(hours=4)
            filename = ('%sF%s') %\
                       (upload_ts.strftime(app.config['FILE_NAME_DT_FORMAT']),
                        secure_filename(f.filename))
            f.save(os.path.join(app.config['IMAGE_FOLDER'], filename))
            # Initialize GridItem and add it to the list
            grid_item = models.GridItem(upload_ts, filename)
            db.session.add(grid_item)
            grid_item.status = models.IMAGESTATUS_NEW
            db.session.commit()
            app.logger.info('Adding image: ' + filename)
            flash('Upload successful.', "upload-success")
        else:
            flash('Upload failed - invalid file extension.', "upload-fail")
    return redirect(url_for('index'))

def allowed_file(filename):
    ext = False
    if '.' in filename:
        ext = filename.rsplit('.', 1)[1]
    return ext in app.config['ALLOWED_EXTENSIONS']

@app.route('/mark_bad/', methods=['GET', 'POST'])
def mark_bad():
    if request.method == 'POST':
        bad_image = request.form['image_id']
        bgi = db.session.query(models.GridItem).\
              filter_by(id=bad_image).first()
        db.session.add(bgi)
        bgi.status = models.IMAGESTATUS_BAD
        db.session.commit()
        flash("Marked an image as bad and removed it.", "removed-bad")
    return redirect(url_for('index'))
    

if __name__ == '__main__':
    app.run(host='0.0.0.0')
