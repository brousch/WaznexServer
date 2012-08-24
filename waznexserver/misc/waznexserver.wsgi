import os
import sys

sys.path.append('/home/ubuntu/WaznexServer')
sys.path.append('/home/ubuntu/WaznexServer/waznexserver')

activate_this = '/home/ubuntu/WaznexServer/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))
from waznexserver import app as application
