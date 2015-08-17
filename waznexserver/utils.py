#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
from waznexserver import db
import models
import config

if __name__ == '__main__':
    # Create data dirs
    data_folders = [df for df in dir(config) if df.endswith('_FOLDER')]
    for folder in data_folders:
        newdir = os.path.abspath(getattr(config, folder))
        print newdir
        if not os.path.exists(newdir):  # If it doesn't exist, try to make it
            try:
                os.mkdir(newdir)
            except OSError:
                print "Unable to create data directory: " + newdir
                print "Error was: %s" % (sys.exc_info()[1],)
                exit(1)
        if not os.path.exists(newdir):  # Make sure it's there now
            print "Unable to find or create data directory: " + newdir
            exit(1)

    # Create database
    db.create_all()

    # Find and add all of the ImageStatuses in models.py
    statuses = [s for s in dir(models) if s.startswith('IMAGESTATUS_')]
    for status in statuses:
        id = getattr(models, status)
        s = models.ImageStatus(id, status.split('_',1)[1])
        db.session.add(s)
    
    # Find and add all of the ImageLevels in models.py
    levels = [l for l in dir(models) if l.startswith('IMAGELEVEL_')]
    for level in levels:
        id = getattr(models, level)
        l = models.ImageLevel(id, level.split('_',1)[1])
        db.session.add(l)
        
    db.session.commit()


#def reload_grid_list_from_disk():
#    # Get list of files from IMAGE_FOLDER and sort by "date" (filename)
#    image_list = os.listdir(app.config['IMAGE_FOLDER'])
#    app.logger.info('Restoring image list from: ' + app.config['IMAGE_FOLDER'])
#    image_list.sort()
#    # Add each image to the grid_list
#    for image in image_list:
#        try:
#            ts_str = image.partition('F')[0]
#            ts = datetime.strptime(ts_str, app.config['DATE_TIME_FORMAT'])
#            grid_item = GridItem(ts, image)
#            grid_item.is_initialized = True
#            grid_list.append(grid_item)
#            app.logger.info('Restored image: ' + image + 
#                            'with timestamp' + ts)
#        except:
#            app.logger.info('Skipped file: ' + image)
#            pass # Skip files with invalid name format
