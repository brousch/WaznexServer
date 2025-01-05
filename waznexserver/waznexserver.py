#!/usr/bin/env python


import os
import datetime

from flask import Flask, Blueprint
from flask import current_app as app  # is this misleading?
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import send_from_directory
from flask import url_for
from sqlalchemy import desc
from sqlalchemy import or_
import timeago
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join

import config
import models
from models import db

main = Blueprint('main', __name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(__name__)
    app.config.from_object(config)
    app.config.from_envvar('WAZNEXSERVER_SETTINGS', silent=True)

    app.register_blueprint(main)

    models.db.init_app(app)

    return app

# https://stackoverflow.com/a/64076444/
@main.app_template_filter('timeago')
def timeago_filter(date):
    return timeago.format(date, datetime.datetime.now())
        
              
@main.route('/')
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
    return render_template('index.html',
                           grid=grid,
                           pretty_dt_format=app.config['PRETTY_DT_FORMAT'])

@main.route('/favicon.ico')
def favicon():
    filename = request.args.get('filename', 'favicon.ico')
    return send_from_directory(os.path.join(app.root_path, 'static', 'favicon'),
                               filename)

@main.route('/thumbnail/<filename>')
def show_thumbnail(filename):
    app.logger.info('Serving thumbnail through Flask: ' + filename)
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename)

@main.route('/medium/<filename>')
def show_downsized(filename):
    app.logger.info('Serving downsized image through Flask: ' + filename)
    return send_from_directory(app.config['DOWNSIZED_FOLDER'], filename)

@main.route('/image/<filename>')
def show_image(filename):
    app.logger.info('Serving image through Flask: ' + filename)
    return send_from_directory(app.config['IMAGE_FOLDER'], filename)

@main.route('/sliced/<dirname>/<filename>')
def show_sliced(dirname, filename):
    app.logger.info('Serving cell image through Flask: ' + filename)
    return send_from_directory(app.config['SPLIT_FOLDER'], safe_join(dirname, filename))

@main.route('/colview/<int:grid_item_id>/<int:col_num>')
def show_colview(grid_item_id, col_num):
    # Get column 0 - Room List
    # Get column col_num
    cells = db.session.query(models.GridCell).\
                filter_by(fk_grid_item=grid_item_id).\
                filter(or_(models.GridCell.col==0,
                           models.GridCell.col==col_num)).\
                order_by('row').order_by('col').all()
    return render_template('colview.html', 
                           cell_list=cells,
                           )

@main.route('/upload/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        if f and allowed_file(f.filename):
            # Name and save file to IMAGE folder
            upload_ts = datetime.datetime.utcnow()
            filename_name, filename_ext = os.path.splitext(f.filename)
            clean_filename = filename_name.replace('.', '') + filename_ext
            filename = ('%sF%s') %\
                       (upload_ts.strftime(app.config['FILE_NAME_DT_FORMAT']),
                        secure_filename(clean_filename))
            f.save(os.path.join(app.config['IMAGE_FOLDER'], filename))
            # Initialize GridItem and add it to the list
            grid_item = models.GridItem(upload_ts, filename)
            db.session.add(grid_item)
            grid_item.status = models.IMAGESTATUS_NEW
            db.session.commit()
            app.logger.info('Adding image: ' + filename)
            flash('Upload successful. Refresh to see it soon', "message-upload-success")
        else:
            flash('Upload failed - invalid file extension.', 
                  "message-upload-fail")
    return redirect(url_for('main.index'))

def allowed_file(filename):
    ext = False
    if '.' in filename:
        ext = filename.rsplit('.', 1)[1]
    return ext in app.config['ALLOWED_EXTENSIONS']

@main.route('/mark_bad/<int:grid_item_id>', methods=['GET'])
def mark_bad(grid_item_id):
    try:
        bgi = db.session.query(models.GridItem).\
              filter_by(id=grid_item_id).first()
        db.session.add(bgi)
        bgi.status = models.IMAGESTATUS_BAD
        db.session.commit()
        flash("Marked an image as bad and removed it.", "message-removed-bad")
    except:
        # Invalid grid_item_id. Ignore it.
        pass
    return redirect(url_for('main.index'))
    

if __name__ == '__main__':
    create_app().run(host='0.0.0.0', port=8080)
