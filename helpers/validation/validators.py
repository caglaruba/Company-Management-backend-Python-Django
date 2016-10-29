from .validationresult import ValidationResult


class RequiredValidator():
    def __init__(self, message=None):
        if not message:
            self.message = "This field is required"
        else:
            self.message = message

    def validate(self, data, instance, database_session):
        if data is None:
            return ValidationResult(False, self.message)
        else:
            return ValidationResult(False)

class UniqueValidator():

    def __init__(self, column, message=None):
        self.column = column

        if not message:
            self.message = "A unique value should be defined"
        else:
            self.message = message

    def validate(self, data, instance, database_session):
        if data is None:
            return ValidationResult(False)

        conflict = database_session.query(self.column.class_).filter(self.column==data).first()
        if conflict and conflict != instance:
            return ValidationResult(False, self.message)
        else:
            return ValidationResult(False)


class IntegerValidator():
    def __init__(self, message=None, stop=False):
        if not message:
            self.message = "A valid integer should be defined"
        else:
            self.message = message

        self.stop = stop

    def validate(self, data, instance, database_session):
        if data is None:
            return ValidationResult(self.stop)

        try:
            int(data)
        except:
            return ValidationResult(self.stop, self.message)
        else:
            return ValidationResult(self.stop)

class EnumValidator():
    def __init__(self, options, message=None):
        self.options =  options

        if not message:
            self.message = "A valid option should be defined"
        else:
            self.message = message

    def validate(self, data, instance, database_session):
        if data is None:
            return ValidationResult(False)

        if data not in self.options:
            return ValidationResult(False, self.message)
        else:
            return ValidationResult(False)


class LengthValidator():
    def __init__(self, min=-1, max=-1, message=None):
        self.min = min
        self.max = max

        if not message:
            self.message = "This field has not the right length"
        else:
            self.message = message

    def validate(self, data, instance, database_session):
        if self.min < 0 and data is None:
            return ValidationResult(False)

        valid = True
        if self.min >= 0 and len(data) < self.min:
            valid = False
        elif self.max >= 0 and len(data) > self.max:
            valid = False

        if valid:
            return ValidationResult(False)
        else:
            return ValidationResult(False, self.message)

class TagIdValidator():
    def __init__(self, min=4, max=14, message=None):
        self.min = min
        self.max = max

        if not message:
            self.message = "This is an invalid TagID"
        else:
            self.message = message

    def validate(self, data, instance, database_session):
        if self.min < 0 and data is None:
            return ValidationResult(False)

        valid = True
        if self.min >= 0 and len(data) < self.min:
            valid = False
        elif self.max >= 0 and len(data) > self.max:
            valid = False

        for letter in data:
            if letter not in "0123456789ABCDEF":
                valid = False

        if valid:
            return ValidationResult(False)
        else:
            return ValidationResult(False, self.message)
