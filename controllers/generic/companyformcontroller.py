import json
import datetime
import decimal

from helpers.validation import validators
from contextlib import closing
from config import Config
from framework.httpexceptions import HttpNotFoundException, HttpUnauthorizedException
from framework.httpexceptions import HttpBadRequestException
from helpers.sqltypeconverter import SqlTypeConverter
from controllers.generic.genericformcontroller import GenericFormController


class CompanyFormController(GenericFormController):

    def __init__(self, model):
        super().__init__(model)


    def handle_get(self, state):
        (request, response, session) = state.unfold()

        if not self.permission_checker.has_permission(state, self.prefix + ".edit"):
            raise HttpUnauthorizedException

        company_id = request.query.get("company_id")
        if company_id:
            company_id = int(company_id)
        if not company_id or not self.permission_checker.can_access_company(state, company_id):
            raise HttpUnauthorizedException

        id_str = request.query.get("id")
        try:
            id = int(id_str)
        except ValueError:
            id = None
        if not id:
            raise HttpBadRequestException()

        with closing(self.database_session_maker()) as database_session:
            instance = database_session.query(self.model).get(id)

            if not instance:
                raise HttpNotFoundException()

            data = self._get_data(instance, database_session)

            response.setJsonBody(json.dumps(data))
            return state

    def handle_submit(self, state):
        (request, response, session) = state.unfold()

        if not self.permission_checker.has_permission(state, self.prefix + ".edit"):
            raise HttpUnauthorizedException

        company_id = request.body.get("company_id")
        if company_id:
            company_id = int(company_id)
        if not company_id or not self.permission_checker.can_access_company(state, company_id):
            raise HttpUnauthorizedException

        with closing(self.database_session_maker(autoflush=False)) as database_session:
            if request.body.get("id"):
                instance = database_session.query(self.model).get(int(request.body["id"]))
                if not instance:
                    raise HttpNotFoundException()
            else:
                instance = self.model()

            result = dict()
            result["errors"] = dict()
            has_errors = False

            for field in self.fields:
                # Do not change read_only fields
                if callable(self.read_only[field]):
                    if self.read_only[field](instance):
                        continue
                elif self.read_only[field]:
                    continue

                raw_data = request.body["data"].get(field, "")

                if self.types[field] == GenericFormController.TYPE_CUSTOM:
                    errors = self.custom_submit[field](self, database_session, instance, raw_data)
                else:
                    data = self._parse_field(field, raw_data, instance, database_session)
                    errors = self._validate_field(field, data, instance, database_session)

                if not errors:
                    if self.types[field] == GenericFormController.TYPE_CUSTOM:
                        # No need to set attribute here, the custom_submit function should take care of any state changes
                        pass
                    else:
                        setattr(instance, field, data)
                else:
                    result["errors"][field] = [error for error in errors]
                    has_errors = True

            (state, instance, result, has_errors) = self.company_after_submit(state, instance, result, has_errors, database_session, company_id)

            result["has_errors"] = has_errors

            if not has_errors:
                database_session.add(instance)
                database_session.commit()

                (instance, result, has_errors) = self.after_commit(instance, result, has_errors, database_session)


                result["data"] = self._get_data(instance, database_session)
                result["id"] = instance.id

            response.setJsonBody(json.dumps(result))

            return state

    def company_after_submit(self, state, instance, result, has_errors, database_session, company_id):


        return (state, instance, result, has_errors)

    def handle_get_form_definition(self, state):
        (request, response, session) = state.unfold()

        if not self.permission_checker.has_permission(state, self.prefix + ".edit"):
            raise HttpUnauthorizedException

        company_id = request.query.get("company_id")
        if company_id:
            company_id = int(company_id)

        with closing(self.database_session_maker()) as database_session:
            if request.query.get("id"):
                instance = database_session.query(self.model).get(int(request.query["id"]))
                if not instance:
                    raise HttpNotFoundException()
            else:
                instance = None

            definition = {}
            definition["fields"] = []

            for name in self.fields:
                field_dict = {}
                field_dict["name"] = name
                field_dict["type"] = self.types[name]
                if callable(self.read_only[name]):
                    field_dict["read_only"] = self.read_only[name](instance)
                else:
                    field_dict["read_only"] = self.read_only[name]
                field_dict["description"] = self.descriptions[name]
                if self.default_value.get(name):
                    if callable(self.default_value[name]):
                        field_dict["default_value"] = self.default_value[name](database_session, instance)
                    else:
                        field_dict["default_value"] = self.default_value[name]
                if self.types[name] == self.TYPE_RELATION:
                    field_dict["large"] = self.large_number_of_options[name]
                    if not self.large_number_of_options[name]:
                        field_dict["options"] = self._get_relation_options(name, database_session, instance, company_id)
                    else:
                        field_dict["options"] = self._get_relation_options_from_instance(name, database_session, instance)

                    field_dict["multiple"] = self.relation_many[name]

                if self.types[name] == self.TYPE_CUSTOM and self.custom_def.get(name):
                    field_dict["data"] = self.custom_def[name](self, database_session, instance)
                elif self.types[name] == SqlTypeConverter.TYPE_ENUM:
                    field_dict["options"] = self._get_enum_options(name)

                definition["fields"].append(field_dict)

            response.setJsonBody(json.dumps(definition))

        return state

    def _get_relation_options(self, name, database_session, instance, company_id, search=None, limit=None):
        if not self.options_search_query.get(name):
            return []

        query = self.options_search_query[name](database_session, instance, search)

        if limit:
            query = query.limit(limit)

        return self._instance_to_options(name, query.all())


