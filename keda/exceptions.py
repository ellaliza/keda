class InvalidFieldConstraintError(Exception):
    pass

class InvalidFieldValueError(Exception):
    pass

class NoPrimaryKeyError(Exception):
    pass

class InvalidFieldError(Exception):
    pass

class MultipleObjectsReturned(Exception):
    pass

class DoesNotExist(Exception):
    pass

class DeletedObjectError(Exception):
    pass
