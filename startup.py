#!./.venv/bin/python3

from django.core.management import ManagementUtility
from dotenv import load_dotenv, get_key, find_dotenv

import os

dotenv_path = find_dotenv()
load_dotenv()

IP = get_key(dotenv_path, "HOST_IP")
PORT = get_key(dotenv_path, "HOST_PORT")
PROD = get_key(dotenv_path, "PROD")
AUTOMIGRATE = get_key(dotenv_path, "AUTOMIGRATE")

os.environ["DJANGO_SETTINGS_MODULE"] = "yubtub.settings"

utility = ManagementUtility(["manage.py", "collectstatic", "--no-input"])
utility.execute()

if IP == None:
    raise NameError("HOST_IP enviroment variable not found")
if PORT == None:
    raise NameError("HOST_PORT enviroment variable not found")
if PROD == None:
    raise NameError("PROD enviroment variable not found")
if AUTOMIGRATE == None:
    raise NameError("AUTOMIGRATE enviroment variable not found")

if AUTOMIGRATE == True:
    print("\nAutomigrate enabled, but you still have to make the migrations yourself.\n")
    utility = ManagementUtility(["manage.py", "migrate"])
    utility.execute()

if PROD == True:
    import multiprocessing
    import gunicorn.app.base

    import yubtub.wsgi

    def number_of_workers():
        return (multiprocessing.cpu_count() * 2) + 1

    class StandaloneApplication(gunicorn.app.base.BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            config = {key: value for key, value in self.options.items()
                    if key in self.cfg.settings and value is not None}
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    options = {
        'bind': '%s:%s' % (IP, PORT),
        'workers': number_of_workers(),
    }
    StandaloneApplication(yubtub.wsgi.application, options).run()
    
else:
    utility = ManagementUtility(["manage.py", "runserver", f"{IP}:{PORT}"])
    utility.execute()