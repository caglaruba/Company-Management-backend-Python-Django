from controllers.generic.genericmodelcontroller import GenericModelController

from models.account import Account


class ListController(GenericModelController):

    def __init__(self):
        super().__init__(Account)

        self.set_id_column(Account.id)

        self.add_column(Account.mailaddress, description="E-mailadres")
        self.add_expression("fullname", Account.firstname + " " + Account.lastname_prefix + " " + Account.lastname, description="Naam")


