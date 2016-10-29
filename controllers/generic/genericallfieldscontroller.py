from controllers.generic.genericcompletecontroller import GenericCompleteController


class GenericAllFieldsController(GenericCompleteController):

    def __init__(self, model):
        super().__init__(model)

    def add_field(self, column, description = None):
        self.list_controller.add_column(column, description)
        self.form_controller.add_field(column, description)

    def bind_routes(self, path, router):
        super().bind_routes(path, router)
