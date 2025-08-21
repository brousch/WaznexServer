# WaznexServer #

*An Online BarCamp Session Grid Viewer*

Waznex Server (What's Next?) is a web application server designed for BarCamp Grand Rapids, but which should be useful for other BarCamps or conferences with a rapidly-changing physical session grid. Its purpose is to host an online version of the meatspace presentation session grid. Essentially, attendees upload a photo of the session grid to the WaznexServer instance:

![photo](assets/photo.jpg)

and the server converts this into an interactive grid:

![grid](assets/grid.png)

This allows attendees to see what's going on in upcoming sessions without going out to the lobby.

Waznex Server is based on the Flask microframework and can easily be hosted on a Linux or OSX server. I currently recommend running in production on Ubuntu with at least 1GB of RAM.


# Installation

## Development

1. Install Docker and git
2. `git clone https://github.com/brousch/WaznexServer.git`
3. `cd WaznexServer`
4. `make docker_dev` (or run Docker commands from Makefile manually)
5. Ctrl-C to stop it.  Re-run it if you make file changes (no shared volumes currently)

## Production on an Ubuntu server

1. SSH to server as root
2. `apt update`
3. `apt install -y make git`
4. `mkdir /opt/waznexserver`
5. `cd /opt/waznexserver`
6. `git clone https://github.com/brousch/WaznexServer.git`
7. `cd WaznexServer`
8. `make init_production`

# Configuration (Optional)

- Modify the image and thumbnail paths found near the top of `config.py` to reflect your file system.
- Modify the `templates/index.html` file to change the page title.
- Modify the `static/css/main.css` file to change the style.
- Also be sure to disable debugging in a live deployment.

# Running

## Development

1. `make docker_dev` or `make docker_dev_debug` if you need flask DEBUG mode.  Or run `python -m waznexserver.waznexserver` in your own Python environment

## Production

1. Make sure DNS is set up to point to the server
2. SSH to server as root
3. `cd /opt/waznexserver/WaznexServer`
4. Set up HTTPS e.g. https://www.linode.com/docs/guides/enabling-https-using-certbot-with-nginx-on-ubuntu
    1. `snap install --classic certbot`
    2. `ln -s /snap/bin/certbot /usr/bin/certbot`
    3. `service nginx stop`
    4. `certbot --nginx`
5. Set up HTTP/2 (just append `http2` to `listen` in `/etc/nginx/sites-available/default`) e.g. https://www.linode.com/docs/guides/how-to-configure-http-2-on-nginx/
6. `make run_production`

# Changelog

## Version 0.8 ##

- Python 2.7 -> 3.12
- Upgrade all python libraries
- Docker instead of Vagrantfile and system services
- Ubuntu 18.04 -> 24.04
- Run splitting code immediately instead of on a cron
- Optimize splitting calls
- Lots of cleanup

## Version 0.7 ##

- responsive full width display
- UI & wording updates
- show relative time since photo uploaded
- caching headers for static files
- auto-rotate iphone images
- system service for splitting the grid
- jinja loop fix
- pip/python2 bootstrap fix

## Version 0.6 ##

- Upgraded to Ubuntu 18.04 Bionic

## Version 0.5 ##

- Switched install from upstart to systemd for Ubuntu 16.04
- Moved to sockets for nginx to waznexserver communication

## Version 0.4 ##

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

- Version 0.1 includes the bare essentials of a working server.
- It can accept file uploads and will display the three most recent uploads using the mobile web theme.
- It generates two additional sized versions of each photo: a downsized version with maximum size of 1024x1024 pixels, and a thumbnail version with a maximum size of 316x316 pixels. The downsized version is useful for viewing on mobile platforms that limit download size (WebOS).  The thumbnail version is sized to fit the mobile theme width.
