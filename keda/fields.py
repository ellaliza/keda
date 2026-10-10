from exceptions import InvalidFieldConstraintError, InvalidFieldValueError
from abc import ABC, abstractmethod

class __DataField(ABC):
    def __init__(self, **kwargs):
        self.field_name: str
        self.default = kwargs.get('default', None)
        self.primary_key : bool = kwargs.get('primary_key', False)
        self.unique : bool = kwargs.get('unique', False)

    
    def set_field_name(self, name):
        self.field_name = name
        

    @property
    @abstractmethod
    def sql_datatype(self):
        pass

    @property
    @abstractmethod
    def column_sql(self):
        pass
        

class CharDataField(__DataField):
    def __init__(self, max_length=255, value: str | None = None , **kwargs):
        super().__init__(**kwargs)
        try:
            self.__validate_max_length(max_length)
        except InvalidFieldConstraintError:
            
            raise InvalidFieldConstraintError
        self.max_length = max_length
        
        if value:
            if len(value) > self.max_length:
                raise InvalidFieldValueError
            self.value: str = value

    def __validate_max_length(self, max_length):
        if max_length > 255:
            raise InvalidFieldConstraintError("Max length of char field cannot be greater than 255")

    @property
    def sql_datatype(self):
        return "TEXT"

    @property
    def column_sql(self):
        return f"{self.field_name} {self.sql_datatype} {"PRIMARY KEY" if self.primary_key else ""} {"UNIQUE" if self.unique else ""}"


class IntDataField(__DataField):
    def __init__(self, value: int | None = None, max_value=None, **kwargs):
        super().__init__(**kwargs)
        if max_value is not None:
            self.max_value = max_value

        if value:
            self.value: int = value

    @property
    def sql_datatype(self):
        return "INTEGER"

    @property
    def column_sql(self):
        return f"{self.field_name} {self.sql_datatype} {"PRIMARY KEY" if self.primary_key else ""} {"UNIQUE" if self.unique else ""}"


class BoolDataField(__DataField):
    def __init__(self, value: bool | None = None, **kwargs):
        super().__init__(**kwargs)
    
        if value:
            self.value: bool = value

    @property
    def sql_datatype(self):
        return "INTEGER"

    @property
    def column_sql(self):
        return f"{self.field_name} {self.sql_datatype} {"PRIMARY KEY" if self.primary_key else ""} {"UNIQUE" if self.unique else ""}"
