import os
import sys
INTERP = os.path.join(os.environ['HOME'], 'talks.barcampgr.org', 'WaznexServer', 'venv', 'bin', 'python')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)
sys.path.append(os.getcwd())
from waznexserver import app as application

