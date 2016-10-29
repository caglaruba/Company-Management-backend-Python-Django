import sys
import os

from framework import Config
from configparser import ConfigParser

from helpers.actiontracker import ActionTracker
from helpers.permissionchecker import PermissionChecker
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import logging


class ConfigLoader():

    def __init__(self):
        self.config_parser = ConfigParser()

    def load_from_path(self, config_path):
        try:
            config_file = open(config_path, "r")
            config_file.close()
        except:
            exit("Could not read config file: " + config_path)

        self.config_parser.read(config_path)
        self.init_config()

    def load_from_default_path(self):
        self.load_from_path("./conf/app.ini")

    def init_config(self):
        config = Config()

        # Read database configuration
        if "database" not in self.config_parser:
            exit("No database section in config found")

        config["database_engine"] = create_engine(self.config_parser.get("database", "url"), echo=self.config_parser.getboolean("database", "echo"))
        config["database_session_maker"] = sessionmaker(bind=config["database_engine"])

        # Read session configuration
        if "session" not in self.config_parser:
            exit("No session section in config found")

        config["session_cookie"] = self.config_parser.get("session", "cookie")
        config["session_httponly"] = self.config_parser.getboolean("session", "httponly")
        config["session_secure"] = self.config_parser.getboolean("session", "secure")
        config["session_lifetime"] = self.config_parser.getint("session", "lifetime")

        # Create permission tracker to track permissions defined in the app
        config["action_tracker"] = ActionTracker()
        config["permission_checker"] = PermissionChecker()

        # Get smtp_server:
        if 'mail' in self.config_parser:
            config["smtp_server"] = self.config_parser.get("mail", "smtp_server")
        else:
            config["smtp_server"] = "localhost"

        logging.basicConfig(format='%(asctime)s %(message)s')






