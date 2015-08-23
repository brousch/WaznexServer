# WaznexServer #

*An Online BarCamp Session Grid Viewer*

Waznex Server (What's Next?) is a web application server designed for BarCamp Grand Rapids, but which should be useful for other BarCamps or conferences with a rapidly-changing physical session grid. Its purpose is to host an online version of the meatspace presentation session grid. Essentially, attendees upload a photo of the session grid to the WaznexServer instance, and the server shows the three most recently uploaded photos. This allows attendees to see what's going on in upcoming sessions without going out to the lobby.

Waznex Server is based on the Flask microframework and can easily be hosted on a Linux or OSX server. I currently recommend running in production on an Ubuntu 14.04 Digital Ocean 1GB instance.

## Version 0.4 (current stable) ##

- Added Vagrant for easier development
- Much improved Makefile for easier development and production installation
- Usable documentation

## Version 0.3 ##

- Newer versions of Flask and dependencies.
- Diagnostic image link between sizes and mark bad.
- Mark bad button.

## Version 0.2 ##

- It now has a database backend using SQLAlchemy instead of the thread-unsafe global list. This has only been tested with Sqlite so far.
- You can now control how many images are shown on the main page - it's no longer hard-coded to 3.

## Version 0.1 ##

### Capabilities ###

- Version 0.1 includes the bare essentials of a working server.
- It can accept file uploads and will display the three most recent uploads using the mobile web theme.
- It generates two additional sized versions of each photo: a downsized version with maximum size of 1024x1024 pixels, and a thumbnail version with a maximum size of 316x316 pixels. The downsized version is useful for viewing on mobile platforms that limit download size (WebOS).  The thumbnail version is sized to fit the mobile theme width.

### Tested on ###

- Ubuntu 14.04 LTS Server

### Installation ###

#### Development ####

1. Install Vagrant and a provider (VirtualBox)
2. Install git
3. `git clone https://github.com/brousch/WaznexServer.git`
4. `cd WaznexServer`
5. `vagrant up`
6. `vagrant ssh`

#### Production on Ubuntu 14.04 64bit ####

1. SSH to server as root
2. `sudo apt-get install -y git`
3. `mkdir /opt/waznexserver`
4. `cd /opt/waznexserver`
5. `git clone https://github.com/brousch/WaznexServer.git`
6. `cd WaznexServer`
7. `make install_system_requirements`
8. `make bootstrap_modern_python_tools`
9. `make create_venv`
10. `make init_data`
11. `make init_production`

### Configuration ###

- Modify the image, downsized, and thumbnail paths found near the top of `config.py` to reflect your file system.
- Modify the `templates/index.html` file to change the page title.
- Modify the `static/css/main.css` file to change the style.
- Also be sure to disable debugging in a live deployment.

### Running ###

#### Development ####

1. `vagrant ssh`
2. `cd /opt/waznexserver/Waznexserver`
3. `make run`

#### Production ####

1. SSH to server as root
2. `cd /opt/waznexserver/WaznexServer`
3. `make run_production`

## Roadmap ##

- Tests
- Ajax refreshing of the grid
- Change slicer from running on a cronjob to pulling off a queue (ZeroMQ
  or whatnot)
- Better documentation
- Create view bad images page
- Data Maintenance and creation scripts:
  - Re-initialize DB based on images on disk
  - Delete photos on disk
  - Re-create downsized and thumbnails images
- Remove excessive hard-coded paths
  - /opt/waznexserver/WaznexServer
  - Python code
  - nginx config
- Automate production deployment    
