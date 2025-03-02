#!/usr/bin/env python

import os
import shutil
import traceback

from PIL import Image
from flask import current_app as app  # is this misleading?

from . import config
from . import models
from .models import db
from . import slice


def run_basic_transforms(grid_image):
    try:
        # Copy orig and create thumbnail version
        app.logger.info('Generating thumbnail for ' + grid_image.filename)
        shutil.copy2(grid_image.get_image_path(), grid_image.get_thumbnail_path())
        thumb = Image.open(grid_image.get_thumbnail_path())
        thumb.thumbnail((316, 316), Image.LANCZOS)
        thumb = thumb.convert('RGB')  # in case PNG with alpha was uploaded
        thumb.save(grid_image.get_thumbnail_path(), "JPEG")

    except Exception:
        print(f"Error while performing basic transforms on {grid_image.filename}")
        traceback.print_exc()
        return False

    return True


def run_gridsplitter(grid_image):
    # Run the splitter for this image
    app.logger.info("Starting to slice: " + grid_image.filename)
    ret_val = slice.main(
        grid_image.get_image_path(),
        config.GRIDSPLITTER_COLOR,
        grid_image.get_split_path(),
        (config.GRIDSPLITTER_CELL_WIDTH, config.GRIDSPLITTER_CELL_HEIGHT),
    )
    # if ret_val:
    # TODO Give slicer.py return values meaningful assignments
    #    print "Unknown error slicing: %s" % (grid_image.filename,)
    #    return False

    # Run verification and sanity checks
    if not verify_gridsplitter(grid_image):
        return False

    app.logger.info("Slice logic done, now saving to db: " + grid_image.filename)

    # Build Cell Grid
    grid_dir = grid_image.get_split_path()
    cells = [c for c in os.listdir(grid_dir) if c.startswith(config.GRIDSPLITTER_CELL_PREFIX)]
    for cell in cells:
        parts = cell.split('.')[0].split("-")
        c = models.GridCell(grid_image.id, cell, int(parts[1]), int(parts[2]))
        db.session.add(c)

    app.logger.info("Successfully sliced: " + grid_image.filename)
    return True


def verify_gridsplitter(grid_image):
    grid_dir = grid_image.get_split_path()

    # Find all of the cell images
    cells = [c for c in os.listdir(grid_dir) if c.startswith(config.GRIDSPLITTER_CELL_PREFIX)]

    # Verify rough count is within MIN and MAX
    min_ct = config.GRIDSPLITTER_MIN_COLS * config.GRIDSPLITTER_MIN_ROWS
    max_ct = config.GRIDSPLITTER_MAX_COLS * config.GRIDSPLITTER_MAX_ROWS
    cell_ct = len(cells)
    if (cell_ct < min_ct) or (cell_ct > max_ct):
        print(("Cell count was out of range %d-%d:%d") % (min_ct, max_ct, cell_ct))
        return False
    # Verify each cell is within MIN and MAX rows and cols
    high_col = -1
    high_row = -1
    for cell in cells:
        parts = cell.split('.')[0].split("-")
        col = int(parts[1])
        row = int(parts[2])
        if col < 0 or col > config.GRIDSPLITTER_MAX_COLS or row < 0 or row > config.GRIDSPLITTER_MAX_ROWS:
            print("Column or row count was incorrect")
            return False
        if col > high_col:
            high_col = col
        if row > high_row:
            high_row = row
    if (high_col < (config.GRIDSPLITTER_MIN_COLS - 1)) or (high_row < (config.GRIDSPLITTER_MIN_ROWS - 1)):
        print("Too few rows or columns found.")
        return False

    # TODO Verify images form an actual grid

    return True


def process_new_images():
    new_grids = db.session.query(models.GridItem).filter_by(status=models.IMAGESTATUS_NEW).order_by('upload_dt').all()

    for g in new_grids:
        process_new(g)

def process_new(g: models.GridItem):
    db.session.add(g)
    g.status = models.IMAGESTATUS_IN_WORK

    try:
        # Do basic image transforms
        basic_result = run_basic_transforms(g)
        if basic_result:
            g.level = models.IMAGELEVEL_BASIC
            print("Basic OK")

            # Do advanced image transforms
            gs_result = run_gridsplitter(g)
            if gs_result:
                g.level = models.IMAGELEVEL_GRID
                print("GridSplitter OK")
            else:
                # Uncomment to mark it bad
                # g.status = models.IMAGESTATUS_BAD
                print("GridSplitter Failed")

            g.status = models.IMAGESTATUS_DONE

        else:
            g.status = models.IMAGESTATUS_BAD
            print("Basic Failed")

    except Exception:
        print(f"Unknown error while processing image: {g.filename}")
        traceback.print_exc()
        g.status = models.IMAGESTATUS_BAD
    finally:
        db.session.commit()

    return g.status


if __name__ == '__main__':
    from .waznexserver import create_app

    app = create_app(initialize_data=False)
    with app.app_context():
        process_new_images()
