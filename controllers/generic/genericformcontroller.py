import json
import datetime
import decimal

from helpers.validation import validators
from contextlib import closing
from config import Config
from framework.httpexceptions import HttpNotFoundException, HttpUnauthorizedException
from framework.httpexceptions import HttpBadRequestException
from helpers.sqltypeconverter import SqlTypeConverter


class GenericFormController():

    TYPE_RELATION = "relation"
    TYPE_CUSTOM = "custom"
    TYPE_EXPRESSION = "expression"

    def __init__(self, model):
        self.config = Config()
        self.database_session_maker = self.config["database_session_maker"]
        self.sqltypeconverter = SqlTypeConverter()

        # Create permission checking tools
        self.action_tracker = self.config["action_tracker"]
        self.permission_checker = self.config["permission_checker"]
        self.prefix = ""

        self.model = model

        self.fields = []
        self.types = {}
        self.descriptions = {}
        self.modifiers = {}
        self.validators = {}
        self.enum_options_list = {}
        self.large_number_of_options = {}
        self.options_class = {}
        self.options_instance_query = {}
        self.options_search_query = {}
        self.option_label_function = {}
        self.is_nullable = {}
        self.relation_many = {}
        self.read_only = {}
        self.default_value = {}

        self.custom_get = {}
        self.custom_submit = {}
        self.custom_def = {}
        self.custom_options = {}

        self.expressions = {}

        self.after_submit = self._default_after_submit
        self.after_commit = self._default_after_commit

    def bind_routes(self, prefix, router):
        self.prefix = prefix
        router.addMapping(r'^/' + prefix + r"/form_field_options/([^/]+)", self.handle_get_options)
        router.addMapping(r"^/" + prefix + r"/form_definition$", self.handle_get_form_definition)
        router.addMapping(r"^/" + prefix + r"/form_get$", self.handle_get)
        router.addMapping(r"^/" + prefix + r"/form_submit", self.handle_submit)

        for action in ["edit"]:
            self.action_tracker.add(prefix + "." + action)



    def add_field(self, column, description=None, validators=None, modifiers=None, label=None, read_only=False, default_value=None):
        self.fields.append(column.key)
        self.types[column.key] = self.sqltypeconverter.from_sql_to_local(column.expression.type)
        self.descriptions[column.key] = description or column.key
        self.validators[column.key] = validators or self._get_default_validators(column)
        self.modifiers[column.key] = modifiers or []
        self.read_only[column.key] = read_only
        if default_value:
            self.default_value[column.key] = default_value
        elif hasattr(column, "default") and column.default is not None and column.default.is_scalar and column.default.arg is not None:
            self.default_value[column.key] = lambda x,y: column.default.arg

        if self.types[column.key] == SqlTypeConverter.TYPE_ENUM:
            self.option_label_function[column.key] = label
            self.enum_options_list[column.key] = list(column.expression.type.enums)
            self.is_nullable[column.key] = not (hasattr(column.expression.type, 'nullable') and not column.expression.type.nullable)

    def add_relation(self, relationship, description=None, validators=None, modifiers = None, options_instance_query=None, options_search_query=None, label=None, nullable=False, many=False, large=False, read_only=False, default_value=None):
        self.fields.append(relationship.key)
        self.types[relationship.key] = "relation"
        self.descriptions[relationship.key] = description or relationship.key
        self.validators[relationship.key] = validators or []
        self.modifiers[relationship.key] = modifiers or []
        self.options_class[relationship.key] = relationship.property.mapper.class_
        self.read_only[relationship.key] = read_only
        if default_value:
            self.default_value[relationship.key] = default_value

        if not options_instance_query:
            self.options_instance_query[relationship.key] = self._get_default_instance_query(relationship.key)
        else:
            self.options_instance_query[relationship.key] = options_instance_query

        if not options_search_query:
            self.options_search_query[relationship.key] = self._get_default_search_query(relationship.key)
        else:
            self.options_search_query[relationship.key] = options_search_query

        self.option_label_function[relationship.key] = label
        self.is_nullable[relationship.key] = nullable
        self.relation_many[relationship.key] = many
        self.large_number_of_options[relationship.key] = large

    def add_custom_field(self, name, get_func, submit_func, description=None, def_func=None, read_only=False):
        self.fields.append(name)
        self.types[name] = GenericFormController.TYPE_CUSTOM
        self.descriptions[name] = description or name
        self.read_only[name] = read_only

        self.custom_get[name] = get_func
        self.custom_submit[name] = submit_func
        if def_func:
            self.custom_def[name] = def_func

    def add_expression_field(self, name, expression, description=None):
        self.fields.append(name)
        self.types[name] = GenericFormController.TYPE_EXPRESSION
        self.descriptions[name] = description or name
        self.read_only[name] = True

        self.expressions[name] = expression


    def handle_get_options(self, state, field):
        (request, response, session) = state.unfold()

        if not self.permission_checker.has_permission(state, self.prefix + ".edit"):
            raise HttpUnauthorizedException

        with closing(self.database_session_maker()) as database_session:
            if (field not in self.fields or self.types[field] != 'relation' or not self.large_number_of_options[field]) and not self.custom_options.get(field):
                raise HttpNotFoundException()

            search = request.query.get("search")

            if request.query.get("id"):
                instance = database_session.query(self.model).get(int(request.query["id"]))
                if not instance:
                    raise HttpNotFoundException()
            else:
                instance = None


            options = self._get_relation_options(field, database_session, instance, search, limit=40)

            response.setJsonBody(json.dumps(options))

            return state



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
                        field_dict["options"] = self._get_relation_options(name, database_session, instance)
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

    def handle_get(self, state):
        (request, response, session) = state.unfold()

        if not self.permission_checker.has_permission(state, self.prefix + ".edit"):
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

    def _get_data(self, instance, database_session):
        data = dict()
        for field in self.fields:
            if self.types[field] == self.TYPE_RELATION:
                if self.relation_many[field]:
                    data[field] = [str(option.id) for option in getattr(instance, field)]
                else:
                    if getattr(instance, field):
                        data[field] = str(getattr(instance, field).id)
                    else:
                        data[field] = ""
            elif self.types[field] == self.TYPE_CUSTOM:
                data[field] = self.custom_get[field](self, database_session, instance)
            elif self.types[field] == self.TYPE_EXPRESSION:
                #TODO: What to do here? We want to bind the instance in the query
                #data[field] = database_session.query(self.expressions[field]).all()
                data[field] = ""
            elif self.types[field] == SqlTypeConverter.TYPE_DATE:
                if getattr(instance, field):
                    data[field] = getattr(instance, field).strftime("%Y-%m-%d")
            elif self.types[field] == SqlTypeConverter.TYPE_DATETIME:
                if getattr(instance, field):
                    data[field] = getattr(instance, field).strftime("%Y-%m-%dT%H:%M:%S")
            elif self.types[field] == SqlTypeConverter.TYPE_CURRENCY:
                if getattr(instance, field):
                    data[field] = '%0.2f' % (getattr(instance, field)/100)
                else:
                    data[field] = '%0.2f' % 0
            elif self.types[field] == SqlTypeConverter.TYPE_DECIMAL:
                if getattr(instance, field):
                    data[field] = ('%0.2f' % getattr(instance, field)).replace(".", ",")
            else:
                data[field] = getattr(instance, field)
        return data


    def handle_submit(self, state):
        (request, response, session) = state.unfold()

        if not self.permission_checker.has_permission(state, self.prefix + ".edit"):
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

            (state, instance, result, has_errors) = self.after_submit(state, instance, result, has_errors, database_session)

            result["has_errors"] = has_errors

            if not has_errors:
                database_session.add(instance)
                database_session.commit()

                (instance, result, has_errors) = self.after_commit(instance, result, has_errors, database_session)


                result["data"] = self._get_data(instance, database_session)
                result["id"] = instance.id

            response.setJsonBody(json.dumps(result))

            return state

    def _default_after_submit(self, state, instance, result, has_errors, database_session):
        return (state, instance, result, has_errors)

    def _default_after_commit(self, instance, result, has_errors, database_session):
        return (instance, result, has_errors)

    def _validate_field(self, field, data, instance, database_session):
        if not self.validators.get(field):
            return []

        error_messages = []
        for validator in self.validators.get(field, []):
            validation_result = validator.validate(data, instance, database_session)

            if validation_result.error_message:
                error_messages.append(validation_result.error_message)

            if validation_result.stop:
                return error_messages

        return error_messages

    def _parse_field(self, field, data, instance, database_session):
        if data is None:
            return None
        if self.types[field] == SqlTypeConverter.TYPE_STRING:
            for modifier in self.modifiers[field]:
                data = modifier(data, instance, database_session)
            return data
        elif self.types[field] == SqlTypeConverter.TYPE_TEXT:
            return data
        elif self.types[field] == SqlTypeConverter.TYPE_INTEGER:
            try:
                return int(data)
            except:
                return "INVALID"
        elif self.types[field] == SqlTypeConverter.TYPE_DECIMAL:
            try:
                return decimal.Decimal(data.replace(",","."))
            except:
                return "INVALID"
        elif self.types[field] == SqlTypeConverter.TYPE_CURRENCY:
            if not data:
                return 0
            try:
                return int(data)*100
            except:
                try:
                    return int(decimal.Decimal(data.replace(",","."))*100)
                except:
                    return "INVALID"

        elif self.types[field] == SqlTypeConverter.TYPE_ENUM:
            if not data:
                return None
            else:
                return data
        elif self.types[field] == SqlTypeConverter.TYPE_DATE:
            if not data:
                return None
            else:
                return datetime.datetime.strptime(data[0:10], "%Y-%m-%d").date()
        elif self.types[field] == SqlTypeConverter.TYPE_DATETIME:
            if not data:
                return None
            else:
                return datetime.datetime.strptime(data, "%Y-%m-%dT%H:%M:%S")
        elif self.types[field] == SqlTypeConverter.TYPE_BOOLEAN:
            if not data:
                return False
            else:
                return True
        elif self.types[field] == self.TYPE_RELATION:
            if self.relation_many[field]:
                return self._get_instances_by_ids(field, database_session, instance, data)
            else:
                instances = self._get_instances_by_ids(field, database_session, instance, [data])
                if instances and len(instances) > 0:
                    return instances[0]
                else:
                    return None

    def _get_instances_by_ids(self, name, database_session, instance, data):
        if not self.options_instance_query.get(name):
            return None


        try:
            ids = [int(id_str) for id_str in data]
        except:
            return None

        instances = self.options_instance_query[name](database_session, instance, ids).all()

        return instances

    def _get_relation_options_from_instance(self, name, database_session, instance):
        if not instance:
            return []
        if self.relation_many[name]:
            option_instances = getattr(instance, name)
        else:
            option_instances = [getattr(instance, name)]

        return self._instance_to_options(name, option_instances)

    def _instance_to_options(self, name, option_instances):
        option_label = self.option_label_function.get(name)
        options = []
        if self.is_nullable.get(name):
            options.append({'id':'', 'description':''})
        for option_instance in option_instances:
            if option_instance is None:
                continue
            option = {}
            option["id"] = str(option_instance.id)
            if option_label:
                option["description"] = option_label(option_instance)
            else:
                option["description"] = str(option_instance)

            options.append(option)

        return options

    def _get_relation_options(self, name, database_session, instance, search=None, limit=None):
        if not self.options_search_query.get(name):
            return []

        query = self.options_search_query[name](database_session, instance, search)

        if limit:
            query = query.limit(limit)

        return self._instance_to_options(name, query.all())


    def _get_enum_options(self, name):
        if not self.enum_options_list.get(name):
            return []

        option_label = self.option_label_function.get(name)
        options = []
        if self.is_nullable.get(name):
            options.append({'id':'', 'description':''})
        for option in self.enum_options_list[name]:
            if option_label:
                options.append({'id':option, 'description':option_label(option)})
            else:
                options.append({'id':option, 'description':option})

        return options

    def _get_default_validators(self, column):
        default_validators = []
        if self.sqltypeconverter.from_sql_to_local(column.expression.type) == SqlTypeConverter.TYPE_INTEGER:
            default_validators.append(validators.IntegerValidator(stop=True))
        elif self.sqltypeconverter.from_sql_to_local(column.expression.type) == SqlTypeConverter.TYPE_CURRENCY:
            default_validators.append(validators.IntegerValidator(stop=True))
        elif self.sqltypeconverter.from_sql_to_local(column.expression.type) == SqlTypeConverter.TYPE_ENUM:
            default_validators.append(validators.EnumValidator(list(column.expression.type.enums)))

        if hasattr(column.expression.type, 'length') and column.expression.type.length:
            default_validators.append(validators.LengthValidator(max=column.expression.type.length))
        if hasattr(column.expression.type, 'nullable') and not column.expression.type.nullable:
            default_validators.append(validators.RequiredValidator())
        if hasattr(column.expression, 'unique') and column.expression.unique:
            default_validators.append(validators.UniqueValidator(column))

        return default_validators

    def _get_default_instance_query(self, relationship_key):
        def options_instance_query(database_session, instance, ids):
            return database_session.query(self.options_class[relationship_key]).filter(self.options_class[relationship_key].id.in_(ids))
        return options_instance_query

    def _get_default_search_query(self, relationship_key):
        def options_search_query(database_session, instance, search):
            return database_session.query(self.options_class[relationship_key])
        return options_search_query
