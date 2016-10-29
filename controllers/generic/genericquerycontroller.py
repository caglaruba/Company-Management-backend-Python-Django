import json
import datetime
from contextlib import closing
from sqlalchemy import desc

from framework import Config
from framework.httpexceptions import HttpBadRequestException, HttpUnauthorizedException
from helpers.sqltypeconverter import SqlTypeConverter


class GenericQueryController():

    def __init__(self, unbound_query = None):
        self.config = Config()
        self.database_session_maker = self.config["database_session_maker"]
        self.sqltypeconverter = SqlTypeConverter()

        self.unbound_query = unbound_query

        self.column_order = []
        self.column_def = {}

        self.default_sort = []

        self.default_filter = {}

        # Create permission checking tools
        self.action_tracker = self.config["action_tracker"]
        self.permission_checker = self.config["permission_checker"]
        self.prefix = ""
        self.permission_prefix = ""


    def build(self):
        self._complete_column_def()

    def get_query(self, database_session, state):
        if database_session:
            return self.unbound_query.with_session(database_session)
        else:
            return self.unbound_query

    def bind_routes(self, prefix, router, permission_prefix = None):
        self.build()
        self.prefix = prefix
        router.addMapping(r"^/" + prefix + r"/definition$", self.handle_get_definition)
        router.addMapping(r"^/" + prefix + r"/data$", self.handle_get_data)
        router.addMapping(r"^/" + prefix + r"/totals$", self.handle_get_totals)
        router.addMapping(r"^/" + prefix + r"/export$", self.handle_get_export)

        if permission_prefix is None:
            self.permission_prefix = prefix
        else:
            self.permission_prefix = permission_prefix

        for action in ["list"]:
            self.action_tracker.add(self.permission_prefix + "." + action)


    def handle_get_definition(self, state):
        (request, response, session) = state.unfold()

        if not self.permission_checker.has_permission(state, self.permission_prefix + ".list"):
            raise HttpUnauthorizedException

        definition = dict()

        # Create column definition
        definition["columns"] = []
        for column_name in self.column_order:
            column_def = {}
            column_def["name"] = column_name
            column_def["type"] = self.column_def[column_name]["type"]
            column_def["hidden"] = self.column_def[column_name]["hidden"]
            column_def["description"] = self.column_def[column_name]["description"]
            definition["columns"].append(column_def)

        # Create order definition
        definition["default_sort"] = []
        for (column_name, sorting) in self.default_sort:
            definition["default_sort"].append(column_name + ":" + sorting)

        definition["default_filter"] = {}
        for column_name in self.default_filter:
            if callable(self.default_filter[column_name]):
                definition["default_filter"][column_name] = self.default_filter[column_name]()
            else:
                definition["default_filter"][column_name] = self.default_filter[column_name]

        response.setJsonBody(json.dumps(definition))

        return state

    def handle_get_data(self, state):
        (request, response, session) = state.unfold()

        if not self.permission_checker.has_permission(state, self.permission_prefix + ".list"):
            raise HttpUnauthorizedException

        # Get database session
        with closing(self.database_session_maker()) as database_session:

            # Bind query to session
            query = self.get_query(database_session, state)

            # Add order, filters and limits
            # Parse limit and offset
            try:
                limit_str = request.query["limit"]
                limit = int(limit_str)
            except:
                limit = None

            try:
                offset_str = request.query["offset"]
                offset = int(offset_str)
            except:
                offset = None

            try:
                sort_str = request.query["sort"]
                sort = [sort_str.split(":")]
            except:
                sort = self.default_sort

            try:
                filter_str = request.query["filter"]
                filter = json.loads(filter_str)
            except:
                filter = None

            if filter:
                query = self._parse_and_apply_filter(filter, query)

            try:
                context_filter_str = request.query["context_filter"]
                context_filter = json.loads(context_filter_str)
            except:
                context_filter = None

            if context_filter:
                query = self._parse_and_apply_context_filter(state, database_session, context_filter, query)

            if sort:
                if sort[0][1] == "DESC":
                    query = query.order_by(desc(self._get_entity_from_query_by_name(query, sort[0][0])))
                else:
                    query = query.order_by(self._get_entity_from_query_by_name(query, sort[0][0]))

            if limit:
                query = query.limit(limit)

            if limit and offset:
                query = query.offset(offset)

            # Execute query
            rows = query.all()


            # Transform query in to row data
            rows_data = []
            for row in rows:
                row_data = {}
                for column in self.column_order:
                    value = self._json_serialize_column_value(column, row.__getattribute__(column))
                    if value and self.column_def[column]["type"] == SqlTypeConverter.TYPE_ENUM:
                        row_data[column] = str(value)
                    else:
                        row_data[column] = value

                rows_data.append(row_data)

            # Convert primitive object to json and write to body
            response.setJsonBody(json.dumps(rows_data))

            return state

    def handle_get_totals(self, state):
        (request, response, session) = state.unfold()

        # Get database session
        with closing(self.database_session_maker()) as database_session:

            # Bind query to session
            query = self.get_query(database_session, state)

            # Get total count
            total_count = query.count()

            # Bind query again to get fresh query
            query = self.get_query(database_session, state)

            # Apply filters
            try:
                filter_str = request.query["filter"]
                filter = json.loads(filter_str)
            except:
                filter = None

            if filter:
                query = self._parse_and_apply_filter(filter, query)

            try:
                context_filter_str = request.query["context_filter"]
                context_filter = json.loads(context_filter_str)
            except:
                context_filter = None

            if context_filter:
                query = self._parse_and_apply_context_filter(state, database_session, context_filter, query)

            # Get filtered count
            filtered_count = query.count()

            # Make return object
            return_obj = {}
            return_obj["total_count"] = total_count
            return_obj["filtered_count"] = filtered_count

            # Write to response body
            response.setJsonBody(json.dumps(return_obj))

            # Close database
            database_session.close()

            return state

    def handle_get_export(self, state):
        (request, response, session) = state.unfold()

        if not self.permission_checker.has_permission(state, self.permission_prefix + ".list"):
            raise HttpUnauthorizedException

        # Get database session
        with closing(self.database_session_maker()) as database_session:

            # Bind query to session
            query = self.get_query(database_session, state)

            # Add order, filters and limits
            # Parse limit and offset
            try:
                sort_str = request.query["sort"]
                sort = [sort_str.split(":")]
                if len(sort[0]) == 1:
                    sort = []
            except:
                sort = self.default_sort

            try:
                filter_str = request.query["filter"]
                filter = json.loads(filter_str)
            except:
                filter = None

            if filter:
                query = self._parse_and_apply_filter(filter, query)

            try:
                context_filter_str = request.query["context_filter"]
                context_filter = json.loads(context_filter_str)
            except:
                context_filter = None

            if context_filter:
                query = self._parse_and_apply_filter(context_filter, query)

            if sort:
                query = query.order_by(sort[0][0] + " " + sort[0][1])

            try:
                show_str = request.query["show"]
                show = json.loads(show_str)
            except:
                show = None

            # Execute query
            rows = query.all()

            # Write rows
            delimiter = "\t"
            seperator = "\n"

            response_data_buf = []
            for column in self.column_order:
                if (show == None and not self.column_def[column]["hidden"]) or (show != None and show[column]):
                    response_data_buf.append(self.column_def[column]["description"])
                    response_data_buf.append(delimiter)

            response_data_buf.append(seperator)

            # Transform query in to row data
            for row in rows:
                for column in self.column_order:
                    if (show == None and not self.column_def[column]["hidden"]) or (show != None and show[column]):
                        response_data_buf.append(self._csv_serialize_column_value(column, row.__getattribute__(column)))
                        response_data_buf.append(delimiter)
                response_data_buf.append(seperator)

            # Convert write to body
            # ToDo: Is this a correct solution for None items in the response_data_buf?
            response.body = "".join(str(x) for x in response_data_buf)
            response.content_type = "text/csv"
            response.headers["Content-Disposition"] = "attachment; filename=export.csv"

            return state

    def _complete_column_def(self):
        # Store column order:
        self.column_order = [column_description["name"] for column_description in self.get_query(None, None).column_descriptions]

        # Store column properties
        for column_description in self.get_query(None, None).column_descriptions:
            # Get the column name
            column_name = column_description["name"]

            # Create an dictionary if it doesn't exist
            if not self.column_def.get(column_name):
                self.column_def[column_name] = {}

            # Store the column type
            self.column_def[column_name]["type"] = self.sqltypeconverter.from_sql_to_local(column_description["type"])

            # Set the display value
            if not self.column_def[column_name].get("hidden"):
                self.column_def[column_name]["hidden"] = False

            # Set the description
            if not self.column_def[column_name].get("description"):
                self.column_def[column_name]["description"] = column_name


    def set_default_sort(self, column_name, sorting):
        if column_name in self.column_def and sorting.upper() in ["ASC", "DESC"]:
            self.default_sort = [(column_name, sorting.upper())]

    def set_default_filter(self, column_name, filter):
        self.default_filter[column_name] = filter

    def set_column_description(self, column_name, description):
        if column_name in self.column_def and description:
            self.column_def[column_name]["description"] = description

    def _json_serialize_column_value(self, column, value):
        if value is None:
            return None
        elif self.column_def[column]["type"] in ["boolean", "integer", "string", "text", "enum"]:
            if self.column_def[column].get("formatter"):
                return self.column_def[column]["formatter"](value)
            return value
        elif self.column_def[column]['type'] in ['currency']:
            return '%0.2f' % (value/100)
        elif self.column_def[column]['type'] in ['decimal']:
            return ('%0.2f' % value).replace(".",",")
        elif self.column_def[column]['type'] in ['date']:
            return value.isoformat() + "Z"
        elif self.column_def[column]['type'] in ['datetime']:
            return value.isoformat() + "Z"
        elif self.column_def[column]['type'] in ['uuid']:
            return str(value)
        elif self.column_def[column]['type'] in ['interval']:
            hours, remainder = divmod(value.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            return "{:.0f}:{:02.0f}".format(hours, minutes)

    def _csv_serialize_column_value(self, column, value):
        if value is None:
            return ""
        if self.column_def[column]["type"] in ["string", "text"]:
            if self.column_def[column].get("formatter"):
                return self.column_def[column]["formatter"](value)
            return value
        elif self.column_def[column]["type"] in ["boolean", "integer"]:
            if self.column_def[column].get("formatter"):
                return self.column_def[column]["formatter"](value)
            return str(value)
        elif self.column_def[column]["type"] in ["currency"]:
            return '%0.2f' % (value/100)
        elif self.column_def[column]['type'] in ['decimal']:
            return ('%0.2f' % value).replace(".",",")
        elif self.column_def[column]['type'] in ['date']:
            return value.isoformat()
        elif self.column_def[column]['type'] in ['datetime']:
            return value.isoformat()
        elif self.column_def[column]['type'] in ['enum']:
            return str(value)
        elif self.column_def[column]['type'] in ['uuid']:
            return str(value)
        elif self.column_def[column]['type'] in ['interval']:
            hours, remainder = divmod(value.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            return "{:.0f}:{:02.0f}".format(hours, minutes)

    def _parse_and_apply_context_filter(self, state, database_session, context_filter, query):
        return self._parse_and_apply_filter(context_filter, query)

    def _parse_and_apply_filter(self, filter, query):
        for column_name in filter:
            if not column_name in self.column_order:
                continue

            column_def = self.column_def[column_name]
            column_type = column_def['type']

            (filter_type, _, filter_value) = filter[column_name].partition(":")

            if column_type in ["string", "text"]:
                if filter_type == 'no_value':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name) == None)
                elif filter_type == 'match':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name) == filter_value)
                elif filter_type == 'like':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name).ilike(filter_value))
                elif filter_type == 'contains':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name).ilike("%"+filter_value+"%"))
                elif filter_type == 'not_match':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name) != filter_value)
                elif filter_type == 'not_like':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name).notilike(filter_value))
                elif filter_type == 'not_contains':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name).notilike("%"+filter_value+"%"))
            elif column_type in ["enum"]:
                if filter_type == 'match':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name) == filter_value)

            elif column_type in ["integer", "currency"]:
                if filter_type == 'in':
                    filter_values = filter_value.split(",")
                    try:
                        filter_values = [int(filter_value) for filter_value in filter_values]
                    except ValueError:
                        continue
                else:
                    try:
                        filter_value = int(filter_value)
                    except ValueError:
                        continue

                if filter_type == 'equals':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name) == filter_value)
                elif filter_type == 'less':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name) < filter_value)
                elif filter_type == 'leq':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name) <= filter_value)
                elif filter_type == 'geq':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name) >= filter_value)
                elif filter_type == 'greater':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name) > filter_value)
                elif filter_type == 'in':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name).in_(tuple(filter_values)))

            elif column_type == "date":
                try:
                    filter_value = datetime.datetime.strptime(filter_value, "%Y-%m-%d")
                except ValueError:
                    continue
                if filter_type == 'equals':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name) == filter_value)
                elif filter_type == 'less':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name) < filter_value)
                elif filter_type == 'leq':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name) <= filter_value)
                elif filter_type == 'geq':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name) >= filter_value)
                elif filter_type == 'greater':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name) > filter_value)
            elif column_type == "datetime":
                if filter_type == 'no_value':
                    query = query.filter(self._get_entity_from_query_by_name(query, column_name) == None)
                else:
                    try:
                        filter_value = datetime.datetime.strptime(filter_value, "%Y-%m-%dT%HH:%MM:%SS")
                    except ValueError:
                        continue
                    if filter_type == 'equals':
                        query = query.filter(self._get_entity_from_query_by_name(query, column_name) == filter_value)
                    elif filter_type == 'less':
                        query = query.filter(self._get_entity_from_query_by_name(query, column_name) < filter_value)
                    elif filter_type == 'leq':
                        query = query.filter(self._get_entity_from_query_by_name(query, column_name) <= filter_value)
                    elif filter_type == 'geq':
                        query = query.filter(self._get_entity_from_query_by_name(query, column_name) >= filter_value)
                    elif filter_type == 'greater':
                        query = query.filter(self._get_entity_from_query_by_name(query, column_name) > filter_value)
        return query


    def _get_entity_from_query_by_name(self, query, column_name):
        for entity in query._entities:
            if entity._label_name == column_name:
                return entity.expr

        return None



