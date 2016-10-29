import sys

from config import ConfigLoader
from app import FirmQApp

# Config_path get from argv (for uwsgi:app) of default one:
if len(sys.argv) > 1:
    config_path = sys.argv[1]
else:
    config_path = "./conf/app.ini"

config_loader = ConfigLoader()
config_loader.load_from_path(config_path)

app = FirmQApp()
wsgi = app.getWsgi()


if __name__ == "__main__":
    print("Serving application at http://localhost:8000")
    app.serve()