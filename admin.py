import argparse
import getpass
import datetime
from contextlib import closing

from config import ConfigLoader
from sqlalchemy import MetaData

import app

from models import Base
from models.account import Account
from models.role import Role
from models.permission import Permission

from framework import Config


parser = argparse.ArgumentParser(description="Process some integers.")
parser.add_argument('action', choices=["create_db", "create_admin", "create_missing_tables"])
parser.add_argument('--config', required=False, type=str, default=None)

args = parser.parse_args()

config_loader = ConfigLoader()

if args.config:
    config_loader.load_from_path(args.config)
else:
    config_loader.load_from_default_path()

config = Config()
database_session_maker = config["database_session_maker"]

def drop_all_tables(engine):
    """
    Fix to enable SQLAlchemy to drop tables even if it didn't know about it.
    :param engine:
    :return:
    """
    meta = MetaData(engine)
    meta.reflect()
    meta.clear()
    meta.reflect()
    meta.drop_all()

if args.action == "create_db":
    database_engine = config["database_engine"]

    drop_all_tables(database_engine)
    Base.metadata.create_all(database_engine)

elif args.action == "create_missing_tables":
    database_engine = config["database_engine"]

    Base.metadata.create_all(database_engine)

elif args.action == "create_admin":
    print("Creating admin account\n")

    password_match = False

    while not password_match:
        password1 = getpass.getpass("Enter password: ")
        password2 = getpass.getpass("Enter password again: ")

        if password1 == password2:
            password_match = True
        else:
            print("Passwords don't match. Try again.\n")

        with closing(database_session_maker()) as database_session:
            account = Account()
            account.firstname = "Admin"
            account.lastname_prefix = ""
            account.lastname = "Admin"
            account.mailaddress = "admin@admin.com"
            account.set_password(password1)

            role = database_session.query(Role).filter(Role.name == "Administrator").first()
            if not role:
                role = Role()
                role.name = "Administrator"
                role.description = "Administrator role"
            account.role = role

            for action in ['role.list','role.edit', 'account.list', 'account.edit']:
                permission = Permission()
                permission.action = action
                permission.role = role

            database_session.add(account)
            database_session.commit()

            print("Created admin account with mailadddress " + account.mailaddress)
