import json
from contextlib import closing

from controllers.generic.genericformcontroller import GenericFormController
from framework.httpexceptions import HttpUnauthorizedException, HttpNotFoundException
from helpers.sqltypeconverter import SqlTypeConverter


class GenericTabFormController(GenericFormController):

    def __init__(self, model):
        super().__init__(model)

        self.tabs = []
        self.tab_names = {}
        self.tab_fields = {}

    def add_tab(self, key, name):
        self.tabs.append(key)
        self.tab_names[key] = name

    def add_field(self, column, description=None, validators=None, modifiers=None, label=None, read_only=False, default_value = None, tab_key=None):
        self.tab_fields[column.key] = tab_key
        super().add_field(column, description, validators, modifiers, label, read_only, default_value)

    def add_relation(self, relationship, description=None, validators=None, modifiers = None, options_instance_query=None,
                     options_search_query=None, label=None, nullable=False, many=False, large=False, read_only=False, default_value=None, tab_key=None):
        self.tab_fields[relationship.key] = tab_key
        super().add_relation(relationship, description, validators, modifiers, options_instance_query, options_search_query, label, nullable, many, large, read_only, default_value)

    def add_custom_field(self, name, get_func, submit_func, description=None, def_func=None, read_only=False, tab_key=None):
        self.tab_fields[name] = tab_key
        super().add_custom_field(name, get_func, submit_func, description, def_func, read_only)

    def add_expression_field(self, name, expression, description=None, tab_key=None):
        self.tab_fields[name] = tab_key
        super().add_expression_field(name, expression, description)

    def handle_get_form_definition(self, state):
        (request, response, session) = state.unfold()

        if not self.permission_checker.has_permission(state, self.prefix + ".edit"):
            raise HttpUnauthorizedException

        with closing(self.database_session_maker()) as database_session:
            if request.query.get("id"):
                instance = database_session.query(self.model).get(int(request.query["id"]))
                if not instance:
                    raise HttpNotFoundException()
            else:
                instance = None

            t = self.translator_creator(state)

            definition = {}
            definition["tabs"] = self.tabs
            definition["tab_names"] = dict([[key, t(tab_name)] for (key, tab_name) in self.tab_names.items()])

            definition["fields"] = []

            for name in self.fields:
                field_dict = {}
                field_dict["name"] = name
                field_dict["tab"] = self.tab_fields[name]
                field_dict["type"] = self.types[name]
                if callable(self.read_only[name]):
                    field_dict["read_only"] = self.read_only[name](instance)
                else:
                    field_dict["read_only"] = self.read_only[name]

                field_dict["description"] = t(self.descriptions[name])
                if self.default_value.get(name):
                    if callable(self.default_value[name]):
                        field_dict["default_value"] = self.default_value[name](database_session, instance)
                    else:
                        field_dict["default_value"] = self.default_value[name]
                if self.types[name] == self.TYPE_RELATION:
                    field_dict["large"] = self.large_number_of_options[name]
                    if not self.large_number_of_options[name]:
                        field_dict["options"] = self._get_relation_options(name, database_session, instance)
                    else:
                        field_dict["options"] = self._get_relation_options_from_instance(name, database_session, instance)

                    field_dict["multiple"] = self.relation_many[name]

                if self.types[name] == self.TYPE_CUSTOM and self.custom_def.get(name):
                    field_dict["data"] = self.custom_def[name](self, database_session, instance)
                elif self.types[name] == SqlTypeConverter.TYPE_ENUM:
                    field_dict["options"] = self._get_enum_options(name, t)

                definition["fields"].append(field_dict)

            response.setJsonBody(json.dumps(definition))

        return state



