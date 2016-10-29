from controllers.generic.genericquerycontroller import GenericQueryController

from sqlalchemy.orm import Query


class GenericModelController(GenericQueryController):

    # SQLAlchemy model that is served by this DataController
    model = None
    columns = None
    column_def = None

    def __init__(self, model):
        super().__init__()
        self.model = model

        self.id_column = None
        self.columns = []
        self.column_def = {}


    def add_column(self, column, description = None, outer_join = False, formatter = None, join_expression = None, hidden = False, key=None):
        key = key or column.key
        self.columns.append(key)
        self.column_def[key] = {}
        self.column_def[key]["column"] = column
        self.column_def[key]["description"] = description or column.key
        self.column_def[key]["outer_join"] = outer_join
        self.column_def[key]["formatter"] = formatter
        self.column_def[key]["join_expression"] = join_expression
        self.column_def[key]["hidden"] = hidden

    def add_expression(self, key, expression, description = None, join_class=None, outer_join = False, formatter = None, join_expression = None, hidden = False):
        self.columns.append(key)
        self.column_def[key] = {}
        self.column_def[key]["expression"] = expression
        self.column_def[key]["description"] = description or key
        self.column_def[key]["join"] = join_class
        self.column_def[key]["outer_join"] = outer_join
        self.column_def[key]["formatter"] = formatter
        self.column_def[key]["join_expression"] = join_expression
        self.column_def[key]["hidden"] = hidden

    def set_id_column(self, column, hidden=True):
        self.id_column = column
        self.column_def[column.key] = {}
        self.column_def[column.key]["column"] = column
        self.column_def[column.key]["hidden"] = hidden


    def get_query(self, database_session, state):
        query = Query(self.id_column)
        already_joined = []
        for column_key in self.columns:
            if self.column_def[column_key].get("column") is not None:
                column = self.column_def[column_key]["column"]
                if column.class_ != self.model:
                    if self.column_def[column_key]["outer_join"]:
                        if self.column_def[column_key]["join_expression"] is not None:
                            query = query.outerjoin(column.class_, self.column_def[column_key]["join_expression"])
                        else:
                            query = query.outerjoin(column.class_)
                    else:
                        if self.column_def[column_key]["join_expression"] is not None:
                            query = query.join(column.class_, self.column_def[column_key]["join_expression"])
                        else:
                            query = query.join(column.class_)

                query = query.add_column(column.label(column_key))
            elif self.column_def[column_key].get("expression") is not None:
                expression = self.column_def[column_key]["expression"]
                if self.column_def[column_key]["join"] is None:
                    query = query.add_column(expression.label(column_key))
                elif self.column_def[column_key]["join"] is not None and not self.column_def[column_key]["outer_join"]:
                    if not self.column_def[column_key]["join"] in already_joined:
                        if self.column_def[column_key]["join_expression"] is not None:
                            query = query.join(self.column_def[column_key]["join"], self.column_def[column_key]["join_expression"])
                        else:
                            query = query.join(self.column_def[column_key]["join"])

                        already_joined.append(self.column_def[column_key]["join"])
                    query = query.add_column(expression.label(column_key))
                elif self.column_def[column_key]["join"] is not None and self.column_def[column_key]["outer_join"]:
                    if not self.column_def[column_key]["join"] in already_joined:
                        if self.column_def[column_key]["join_expression"] is not None:
                            query = query.outerjoin(self.column_def[column_key]["join"], self.column_def[column_key]["join_expression"])
                        else:
                            query = query.outerjoin(self.column_def[column_key]["join"])

                        already_joined.append(self.column_def[column_key]["join"])
                    query = query.add_column(expression.label(column_key))

        if database_session:
            return query.with_session(database_session)
        else:
            return query






