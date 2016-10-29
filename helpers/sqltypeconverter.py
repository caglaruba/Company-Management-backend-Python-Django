import datetime


class SqlTypeConverter():

    TYPE_STRING = "string"
    TYPE_TEXT = "text"
    TYPE_INTEGER = "integer"
    TYPE_CURRENCY = "currency"
    TYPE_DECIMAL = "decimal"
    TYPE_DATE = "date"
    TYPE_INTERVAL = "interval"
    TYPE_DATETIME = "datetime"
    TYPE_BOOLEAN = "boolean"
    TYPE_ENUM = "enum"
    TYPE_UUID = "uuid"

    def __init__(self):
        pass

    def from_sql_to_local(self, sql_type):
        if hasattr(sql_type, 'enums'):
            return SqlTypeConverter.TYPE_ENUM

        try:
            if sql_type.python_type == datetime.timedelta:
                return SqlTypeConverter.TYPE_INTERVAL
        except NotImplementedError:
            pass

        sql_type = str(sql_type)
        if sql_type.startswith("VARCHAR"):
            return SqlTypeConverter.TYPE_STRING
        elif sql_type.startswith("TEXT"):
            return SqlTypeConverter.TYPE_TEXT
        elif sql_type.startswith("INTEGER"):
            return SqlTypeConverter.TYPE_INTEGER
        elif sql_type.startswith("DATETIME"):
            return SqlTypeConverter.TYPE_DATETIME
        elif sql_type.startswith("DATE"):
            return SqlTypeConverter.TYPE_DATE
        elif sql_type.startswith("DECIMAL") or sql_type.startswith("NUMERIC"):
            return SqlTypeConverter.TYPE_DECIMAL
        elif sql_type.startswith("BOOLEAN"):
            return SqlTypeConverter.TYPE_BOOLEAN
        elif sql_type.startswith("UUID"):
            return SqlTypeConverter.TYPE_UUID
        else:
            return ""