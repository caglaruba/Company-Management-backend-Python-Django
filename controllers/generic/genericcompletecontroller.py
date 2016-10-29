from controllers.generic.genericformcontroller import GenericFormController
from controllers.generic.genericmodelcontroller import GenericModelController


class GenericCompleteController():

    def __init__(self, model):
        self.list_controller = GenericModelController(model)
        self.list_controller.set_id_column(model.id)

        self.form_controller = GenericFormController(model)


    def bind_routes(self, path, router):
        self.list_controller.bind_routes(path, router)
        self.form_controller.bind_routes(path, router)