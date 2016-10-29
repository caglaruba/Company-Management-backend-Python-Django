from controllers.generic.genericmodelcontroller import GenericModelController

from models.company import Company


class ListController(GenericModelController):

    def __init__(self):
        super().__init__(Company)

        self.set_id_column(Company.id)

        self.add_column(Company.name, "Naam")


