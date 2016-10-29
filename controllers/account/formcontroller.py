from controllers.generic.genericformcontroller import GenericFormController

from models.account import Account

class FormController(GenericFormController):
    def __init__(self):
        super().__init__(Account)

        self.add_field(Account.mailaddress, "E-mailadres")
        self.add_field(Account.firstname, "Voornaam")
        self.add_field(Account.lastname_prefix, "Voorvoegsel")
        self.add_field(Account.lastname, "Achternaam")

        def role_option_label(instance):
            return instance.name
        self.add_relation(Account.role, "Rol", label=role_option_label)

        def company_option_label(instance):
            return instance.name
        self.add_relation(Account.companies, "Bedrijven", many=True, label=company_option_label)

        def password_get_func(controller, database_session, instance):
            return {}

        def password_parse_func(controller, database_session, instance, data):
            errors = []

            if not data:
                data = {}

            action = data.get("action", "")

            if action == "reset":
                # TODO: Send new e-mail with password
                errors.append(_("Not available yet!"))
            elif action == "change":
                new_password = data.get("new_password", "")
                new_password_repeat = data.get("new_password_repeat", "")

                if len(new_password) < 6:
                    errors.append(_("Password is too short. The password should have at least 6 characters"))
                if new_password != new_password_repeat:
                    errors.append(_("Passwords don't match."))

                if not errors:
                    instance.set_password(new_password)

            return errors

        self.add_custom_field("password", password_get_func, password_parse_func, description="Wachtwoord")

