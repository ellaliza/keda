from exceptions import InvalidFieldConstraintError, InvalidFieldValueError
from abc import ABC, abstractmethod
from datetime import datetime, date

class __DataField(ABC):
    def __init__(self, **kwargs):
        self.field_name: str
        self.default = kwargs.get('default', None)
        self.primary_key : bool = kwargs.get('primary_key', False)
        self.unique : bool = kwargs.get('unique', False)
        self.allow_null : bool = kwargs.get("null", False)

    
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

    @abstractmethod
    def validate_value(self):
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
    allowed_types = (str,)
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
        return f"{self.field_name} {self.sql_datatype} {"UNIQUE" if self.unique else ""} {'NOT NULL' if not self.allow_null else ''}"

    @property
    def py_representation_type(self):
        return str

    def validate_value(self, value):
        if value is None and self.allow_null:
            return True
        if type(value) not in self.allowed_types:
            raise ValueError(f"Value for `{self.field_name}` must be one of the following types: {", ".join([str(t) for t in self.allowed_types])}. Value provided: {value} of type {str(type(value))}")
        try:
            str(value)
        except ValueError:
            raise ValueError(f"Value for `{self.field_name}` must a be string or compatible with string conversion")
        if len(value) > self.max_length:
            raise InvalidFieldValueError(f"Value given must not exceed max_length of {self.max_length}. Value: {value} is {len(value)} chars")
                 
        return True
        
    
class IntDataField(__DataField):
    allowed_types = (float, int, str)
    def __init__(self, max_value=None, min_value: int | None = None,  **kwargs):
        super().__init__(**kwargs)
        
        self.max_value = max_value
        self.min_value = min_value
        self._explicit_auto_inc = "auto_increment" in kwargs
        self.auto_increment: bool = kwargs.get("auto_increment", False)



    @property
    def sql_datatype(self):
        return "INTEGER"

    @property
    def column_sql(self):
        return f"{self.field_name} {self.sql_datatype} {"UNIQUE" if self.unique else ""} {'NOT NULL' if not self.allow_null else ''}"

    @property
    def py_representation_type(self):
        return int

    def validate_value(self, value):
        if value is None and (self.allow_null or self.auto_increment):
            return True
        if type(value) not in self.allowed_types:
            raise ValueError(f"Value for `{self.field_name}` must be one of the following types: {", ".join([str(t) for t in self.allowed_types])}. Value provided: {value} of type {str(type(value))}")
        try:
            int(value)
        except ValueError:
            raise ValueError(f"Value for `{self.field_name}` must a be float or compatible with float conversion")
        if self.max_value is not None and value > self.max_value:
            raise InvalidFieldValueError(f"Value given must not exceed max_value of {self.max_value}. Value: {value}")
        if self.min_value is not None and value < self.min_value:
            raise InvalidFieldValueError(f"Value given must not be below min_value of {self.min_value}. Value: {value}")
                    
        return True

    
class BooleanDataField(__DataField):
    allowed_types = (bool, int, float)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.primary_key = False
        


    @property
    def sql_datatype(self):
        return "BOOLEAN"

    @property
    def column_sql(self):
        return f"{self.field_name} {self.sql_datatype} {"UNIQUE" if self.unique else ""} {'NOT NULL' if not self.allow_null else ''}"

    @property
    def py_representation_type(self):
        return bool

    def validate_value(self, value):
        if value is None and self.allow_null:
            return True
        if type(value) not in self.allowed_types:
            raise ValueError(f"Value for `{self.field_name}` must be of one of these types: {", ".join([str(t) for t in self.allowed_types])}. Value provided: {value} of type {str(type(value))}")
        try:
            if type(value) == int or type(value) == float:
                date.fromtimestamp(value)
            if type(value) == str:
                date.fromisoformat(value)
            if type(value) == bool:
                pass
                
        except ValueError:
            raise ValueError(f"Value for `{self.field_name}` must a be datetime object or compatible with datetime conversion")
                   
        return True



class DateDataField(__DataField):
    allowed_types = (date, datetime, str, int, float)
    def __init__(self,  **kwargs):
        super().__init__(**kwargs)
        

    @property
    def sql_datatype(self):
        return "TEXT"

    @property
    def column_sql(self):
        return f"{self.field_name} {self.sql_datatype} {'UNIQUE' if self.unique else ''} {'NOT NULL' if not self.allow_null else ''}"

    @property
    def py_representation_type(self):
        return date

    def validate_value(self, value):
        if value is None and self.allow_null:
            return True
        if type(value) not in self.allowed_types:
            raise ValueError(f"Value for `{self.field_name}` must be of one of these types: {", ".join([str(t) for t in self.allowed_types])}. Value provided: {value} of type {str(type(value))}")
                
        try:
            if type(value) == int or type(value) == float:
                date.fromtimestamp(value)
            if type(value) == str:
                date.fromisoformat(value)
            if type(value) == datetime:
                date.fromisoformat(value.isoformat().split("T")[0])
            if type(value) == date:
                pass
                
        except ValueError:
            raise ValueError(f"Value for `{self.field_name}` must a be datetime object or compatible with datetime conversion")
        # if self.max_value is not None and value > self.max_value:
        #     raise InvalidFieldValueError(f"Value given must not exceed max_value of {self.max_value}. Value: {value}")
        # if self.min_value is not None and value < self.min_value:
        #     raise InvalidFieldValueError(f"Value given must not be below min_value of {self.min_value}. Value: {value}")
                    
        return True

    
        

class DatetimeDataField(__DataField):
    allowed_types = (datetime, date,  str, int, float)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        


    @property
    def sql_datatype(self):
        return "TEXT"

    @property
    def column_sql(self):
        return f"{self.field_name} {self.sql_datatype}  {"UNIQUE" if self.unique else ""} {'NOT NULL' if not self.allow_null else ''}"

    @property
    def py_representation_type(self):
        return datetime

    def validate_value(self, value):
        if value is None and self.allow_null:
            return True
        if type(value) not in self.allowed_types:
            raise ValueError(f"Value for `{self.field_name}` must be one of the following types: {", ".join([str(t) for t in self.allowed_types])}. Value provided: {value} of type {str(type(value))}")
        try:
            if type(value) == int or type(value) == float:
                datetime.fromtimestamp(value)
            if type(value) == str:
                datetime.fromisoformat(value)
            if type(value) == date:
                datetime.fromisoformat(value.isoformat())
            if type(value) == datetime:
                pass
                
        except ValueError:
            raise ValueError(f"Value for `{self.field_name}` must a be datetime object or compatible with datetime conversion")
        # if self.max_value is not None and value > self.max_value:
        #     raise InvalidFieldValueError(f"Value given must not exceed max_value of {self.max_value}. Value: {value}")
        # if self.min_value is not None and value < self.min_value:
        #     raise InvalidFieldValueError(f"Value given must not be below min_value of {self.min_value}. Value: {value}")
                    
        return True

    
        
class FloatDataField(__DataField):
    allowed_types = (float, int, str)
    def __init__(self, max_value=None, min_value=None,  **kwargs):
        super().__init__(**kwargs)
        try:
            self.max_value = float(max_value) if max_value is not None else None
        except ValueError:
            raise ValueError("max_value must be a float or convertable to float")
        try:
            self.min_value = float(min_value) if min_value is not None else None
        except ValueError:
            raise ValueError("min_value must be a float or compatible with float")
        

    @property
    def sql_datatype(self):
        return "REAL"

    @property
    def column_sql(self):
        return f"{self.field_name} {self.sql_datatype}  {"UNIQUE" if self.unique else ""} {'NOT NULL' if not self.allow_null else ''}"

    @property
    def py_representation_type(self):
        return float

    def validate_value(self, value):
        if value is None and self.allow_null:
            return True
        if type(value) not in self.allowed_types:
            raise ValueError(f"Value for `{self.field_name}` must be one of the following types: {", ".join([str(t) for t in self.allowed_types])}. Value provided: {value} of type {str(type(value))}")
        try:
            float(value)
        except ValueError:
            raise ValueError(f"Value for `{self.field_name}` must a be float or compatible with float conversion")
        if self.max_value is not None and value > self.max_value:
            raise InvalidFieldValueError(f"Value given must not exceed max_value of {self.max_value}. Value: {value}")
        if self.min_value is not None and value < self.min_value:
            raise InvalidFieldValueError(f"Value given must not be below min_value of {self.min_value}. Value: {value}")
                    
        return True
        
