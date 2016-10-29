import sys

from config import ConfigLoader

from framework.application import Application
from framework.router import Router
from framework.config import Config

from helpers.sessionrepository import SessionRepository

from controllers.logincontroller import LoginController
from controllers.rolecontroller import RoleController
from controllers.account.listcontroller import ListController as AccountListController
from controllers.account.formcontroller import FormController as AccountFormController
from controllers.company.listcontroller import ListController as CompanyListController
from controllers.company.formcontroller import FormController as CompanyFormController


class FirmQApp(Application):
    def __init__(self):
        super().__init__()

        self.router = Router()
        self.controller = self.router
        self.config = Config()
        self._session_repository = SessionRepository()

        login_controller = LoginController()
        login_controller.bind_routes("login", self.router)

        role_controller = RoleController()
        role_controller.bind_routes("role", self.router)

        account_form_controller = AccountFormController()
        account_form_controller.bind_routes("account", self.router)
        account_list_controller = AccountListController()
        account_list_controller.bind_routes("account", self.router)

        company_form_controller = CompanyFormController()
        company_form_controller.bind_routes("company", self.router)
        company_list_controller = CompanyListController()
        company_list_controller.bind_routes("company", self.router)


        def redirect_to_index(state):
            (request, response, session) = state.unfold()
            response.setRedirect("/index.html")
            return state

        self.router.addMapping(r"^/$", redirect_to_index)

        self.router.addStaticMapping(r"^/static/", "../client/dist")
        self.router.addStaticMapping(r"^/", "../client/dist")



