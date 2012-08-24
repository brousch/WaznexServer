# WaznexServer #

*An Online BarCamp Session Grid Viewer*

Waznex Server (What's Next?) is a web application server designed for BarCamp
Grand Rapids, but which should be useful for other BarCamps or conferences with
a rapidly-changing physical session grid. Its purpose is to host an online
version of the meatspace presentation session grid. Essentially, attendees
upload a photo of the session grid to the WaznexServer instance, and the server
shows the three most recently uploaded photos. This allows attendees to see
what's going on in upcoming sessions without going out to the lobby.

Waznex Server is based on the Flask microframework and can easily be hosted on
a Linux or OSX server. I recommend an Ubuntu LTS EC2 instance. It will probably
also work on a Windows server, but this has not been tested.

A Waznex Android client based on the PhoneGap framework will soon be available.

## Version 0.3 (current stable) ##

### Changes from 0.2 ###

Newer versions of Flask and dependencies. Diagnostic image link between sizes
and mark bad. Mark bad button.

## Version 0.2 (current stable) ##

### Changes from 0.1 ###

It now has a database backend using SQLAlchemy instead of the thread-unsafe 
global list. This has only been tested with Sqlite so far. You can now control
how many images are shown on the main page - it's no longer hard-coded to 3.

## Version 0.1 ##

### Capabilities ###

Version 0.1 includes the bare essentials of a working server. It can accept
file uploads and will display the three most recent uploads using the mobile
web theme. It generates two additional sized versions of each photo: a
downsized version with maximum size of 1024x1024 pixels, and a thumbnail
version with a maximum size of 316x316 pixels. The downsized version is useful
for viewing on mobile platforms that limit download size (WebOS).  The
thumbnail version is sized to fit the mobile theme width.

### Limitations ###

- If a blurry or innappropriate photo is uploaded, it will show until new
  photos bump it off of the recent list.

### Tested on ###

- Ubuntu 12.04 LTS Server
- Dreamhost

### Installation ###

#### Ubuntu 10.04 LTS Server ####

`sudo apt-get install python-virtualenv python-dev mercurial python-imaging
libjpeg libjpeg-dev`
`virtualenv --no-site-packages --distribute WaznexServer`
`cd WaznexServer`
`source bin/activate`
`pip install flask`
`pip install flask-sqlalchemy`
`pip install pil`
`hg clone http://hg.code.sf.net/p/waznexserver/code waznexserver`

#### Ubuntu 11.04 ####

`sudo apt-get install python-virtualenv python-dev mercurial python-imaging
libjpeg libjpeg-dev`
`virtualenv --no-site-packages --distribute WaznexServer`
`cd WaznexServer`
`source bin/activate`
`pip install flask`
`pip install flask-sqlalchemy`
`pip install pil`
`hg clone http://hg.code.sf.net/p/waznexserver/code waznexserver`
`sudo ./waznexserver/misc/fix_virtualenv_pil.sh`

### Configuration ###

Modify the image, downsized, and thumbnail paths found near the top of
`main.py` to reflect your file system. Modify the `templates/index.html` file
to change the page title. Modify the `static/css/main.css` file to change the
style.  Also be sure to disable debugging in a live deployment.

### Running ###

#### Flask web server ####

python main.py

#### Serving photos and static files using Apache and mod_wsgi ####

`sudo apt-get install libapache2-mod-wsgi`

Although Waznex Server includes a way to serve photos and static files such as
css and javascript using the Flask framework, a more efficient way of serving
them is to use a dedicated web server such as Apache. An example Apache vhost
configuration is included in `misc/example_apache_vhost.txt`.

## Roadmap ##

- Ability for users to vote down a photo so it will be removed from the recent
  list. This should help with pranksters who upload inappropriate photos as
  well as get rid of obscured or blurry photos.
- A smart grid splitter that will slice up the session grid into columns for
  easier viewing on mobil devices.
- Include a copy of or link to the Waznex Android client (coming soon!) for
  download from the site.
- Also see TODO

