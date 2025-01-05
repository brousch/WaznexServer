# A script to upload a bunch of images to see how your server
# handles the load.
#
# Based on http://atlee.ca/software/poster/
# https://bitbucket.org/chrisatlee/poster
import os
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib.request, urllib.error, urllib.parse

UPLOADS_PATH = "/home/ben/Projects/WaznexServer/waznexserver/tests/hammeruploads/uploads"
UPLOAD_URL = "http://waznex-dev.clusterbleep.net/upload/"

def upload_images():
    # Get list of files from IMAGE_FOLDER and sort by "date" (filename)
    image_list = os.listdir(UPLOADS_PATH)
    for image in image_list:
        try:
            print("Uploading: " + image)
            register_openers()
            datagen, headers = multipart_encode({"file": open(UPLOADS_PATH + '/' + image, "rb")})
            request = urllib.request.Request(UPLOAD_URL, datagen, headers)
            print(urllib.request.urlopen(request).read())
        except:
            pass # Skip files that don't work
        
if __name__ == '__main__':
    upload_images()
    