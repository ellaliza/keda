from exceptions import InvalidFieldConstraintError, InvalidFieldValueError
from abc import ABC, abstractmethod
from datetime import datetime, date

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
    def py_representation_type(self):
        pass

    
    @property
    @abstractmethod
    def column_sql(self):
        pass
        
class FieldValue:
    def __init__(self, py_representation_type: type, value = None):
        self.value = value
        self._modified = True
        self.old_value = None
        self.py_representation_type = py_representation_type

    def py_representation(self):
        try:
            return self.py_representation_type(self.value)
        except TypeError:
            return None

    def __str__(self):
        return str(self.value) 

        
class CharDataField(__DataField):
    def __init__(self, max_length=255, **kwargs):
        super().__init__(**kwargs)
        try:
            self.__validate_max_length(max_length)
        except InvalidFieldConstraintError:
            
            raise InvalidFieldConstraintError
        self.max_length = max_length
        

    def __validate_max_length(self, max_length):
        if max_length > 255:
            raise InvalidFieldConstraintError("Max length of char field cannot be greater than 255")

    @property
    def sql_datatype(self):
        return "TEXT"

    @property
    def column_sql(self):
        return f"{self.field_name} {self.sql_datatype} {"PRIMARY KEY" if self.primary_key else ""} {"UNIQUE" if self.unique else ""}"

    @property
    def py_representation_type(self):
        return str
    
class IntDataField(__DataField):
    def __init__(self, max_value=None, **kwargs):
        super().__init__(**kwargs)
        if max_value is not None:
            self.max_value = max_value


    @property
    def sql_datatype(self):
        return "INTEGER"

    @property
    def column_sql(self):
        return f"{self.field_name} {self.sql_datatype} {"PRIMARY KEY" if self.primary_key else ""} {"UNIQUE" if self.unique else ""}"

    @property
    def py_representation_type(self):
        return int


class BooleanDataField(__DataField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.primary_key = False
       

    @property
    def sql_datatype(self):
        return "BOOLEAN"

    @property
    def column_sql(self):
        return f"{self.field_name} {self.sql_datatype} {"PRIMARY KEY" if self.primary_key else ""} {"UNIQUE" if self.unique else ""}"

    @property
    def py_representation_type(self):
        return bool



class DateDataField(__DataField):
    def __init__(self,  **kwargs):
        super().__init__(**kwargs)
        


    @property
    def sql_datatype(self):
        return "TEXT"

    @property
    def column_sql(self):
        return f"{self.field_name} {self.sql_datatype} {"PRIMARY KEY" if self.primary_key else ""} {"UNIQUE" if self.unique else ""}"

    @property
    def py_representation_type(self):
        return date

    def py_representation(self, field_value_obj : FieldValue):
        try:
            return date(field_value_obj.value).isoformat()
        except TypeError:
            return str(None)
    
        

class DatetimeDataField(__DataField):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        


    @property
    def sql_datatype(self):
        return "TEXT"

    @property
    def column_sql(self):
        return f"{self.field_name} {self.sql_datatype} {"PRIMARY KEY" if self.primary_key else ""} {"UNIQUE" if self.unique else ""}"

    @property
    def py_representation_type(self):
        return datetime

    def py_representation(self, field_value_obj : FieldValue):
        try:
            return datetime(field_value_obj.value).isoformat()
        except TypeError:
            return str(None)
    
        
class FloatDataField(__DataField):
    def __init__(self,  **kwargs):
        super().__init__(**kwargs)
        

    @property
    def sql_datatype(self):
        return "REAL"

    @property
    def column_sql(self):
        return f"{self.field_name} {self.sql_datatype} {"PRIMARY KEY" if self.primary_key else ""} {"UNIQUE" if self.unique else ""}"

    @property
    def py_representation_type(self):
        return float