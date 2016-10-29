from contextlib import closing
from repoze.lru import lru_cache

from framework import Config

from models.permission import Permission


class PermissionChecker():

    def __init__(self):
        self.database_session_maker = Config()["database_session_maker"]

    def has_permission(self, state, action):
        if state.session.get("user", {}).get("role_id") is not None:
            return action in self.get_permissions(state.session["user"]["role_id"])
        else:
            return False

    def has_all_permissions(self, state, action_list):
        if state.session.get("user", {}).get("role_id") is not None:
            return all(action in self.get_permissions(state.session["user"]["role_id"]) for action in action_list)
        else:
            return False

    def has_any_permission(self, state, action_list):
        if state.session.get("user", {}).get("role_id") is not None:
            return any(action in self.get_permissions(state.session["user"]["role_id"]) for action in action_list)
        else:
            return False

    def is_role_allowed(self, role_id, action):
        return action in self.get_permissions(role_id)

    def can_access_company(self, state, company_id):
        if state.session.get("user", {}).get("companies") is not None:
            return any(company_id == company['id'] for company in state.session["user"]["companies"])
        else:
            return False

    @lru_cache(maxsize=1000, timeout=60*5)
    def get_permissions(self, role_id):
        with closing(self.database_session_maker()) as database_session:
            permissions = database_session.query(Permission).filter(Permission.role_id == role_id).all()

            return [permission.action for permission in permissions]

