from contextlib import closing
import json
import datetime
from sqlalchemy import func

from framework import Config
from framework.httpexceptions import HttpNotFoundException
from framework.httpexceptions import HttpUnauthorizedException
from models.account import Account


class LoginController():

    def __init__(self):
        self.config = Config()
        self.database_session_maker = self.config["database_session_maker"]

    def handle_do_login(self, state):
        (request, response, session) = state.unfold()

        username = request.body.get("username", "")
        with closing(self.database_session_maker()) as database_session:
            account = database_session.query(Account).filter(Account.mailaddress==username).first()
            if not account:
                raise HttpUnauthorizedException()

            if account.is_password(request.body.get("password", "")):
                session["user"] = account.to_dict()

                response_data = account.to_dict()
                response_data["permissions"] = self.config["permission_checker"].get_permissions(account.role_id)

                response.setJsonBody(json.dumps(response_data))
            else:
                raise HttpUnauthorizedException()

        return state

    def handle_do_logout(self, state):
        (request, response, session) = state.unfold()

        session["user"] = {}

        session.expires = datetime.datetime.utcfromtimestamp(0)

        return state

    def handle_get_login(self, state):
        (request, response, session) = state.unfold()

        response_data = session.get("user", {})
        if session.get("user"):
            response_data["permissions"] = self.config["permission_checker"].get_permissions(session["user"]["role_id"])
        response.setJsonBody(json.dumps(response_data))

        return state

    def bind_routes(self, prefix, router):
        router.addMapping(r'^/' + prefix + r"/login", self.handle_get_login, ["GET"])
        router.addMapping(r'^/' + prefix + r"/login", self.handle_do_login, ["POST"])
        router.addMapping(r'^/' + prefix + r"/logout", self.handle_do_logout, ["POST"])
