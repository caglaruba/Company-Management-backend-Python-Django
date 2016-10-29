from controllers.generic.genericcompletecontroller import GenericCompleteController
from models.role import Role
from models.permission import Permission
from helpers.validation import validators


class RoleController(GenericCompleteController):

    def __init__(self):
        super().__init__(Role)

        self.list_controller.add_column(Role.name, "Rol")

        self.form_controller.add_field(Role.name, "Naam")
        self.form_controller.add_field(Role.description, "Omschrijving")

        def permissions_get_func(controller, database_session, instance):
            data = {}

            data["all"] = self.form_controller.config["action_tracker"].list()
            data["enabled"] = [permission.action for permission in instance.permissions]

            return data

        def permissions_parse_func(controller, database_session, instance, data):
            errors = []

            if not data:
                data = {}

            if data.get("enabled") is not None:
                enabled = data["enabled"]

                instance.permissions = []

                for action in enabled:
                    permission = Permission()
                    permission.action = action
                    permission.role = instance

                    database_session.add(permission)

            return errors

        self.form_controller.add_custom_field("permissions", permissions_get_func, permissions_parse_func, description="Rechten")


