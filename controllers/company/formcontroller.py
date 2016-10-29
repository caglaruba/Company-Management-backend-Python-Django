from controllers.generic.genericformcontroller import GenericFormController

from models.company import Company

class FormController(GenericFormController):
    def __init__(self):
        super().__init__(Company)

        self.add_field(Company.name, "Naam")
