from dataclasses import dataclass
from typing import dataclass_transform
from exceptions import NoPrimaryKeyError, InvalidFieldValueError, DoesNotExist,InvalidFieldError, MultipleObjectsReturned, DeletedObjectError
from database_wrapper import Database
from fields import FieldValue, __DataField, IntDataField
from colored import Text
import inspect
db = Database()

class MetaData():
    use_auto_id = False
    model_name: str
    class_attrs : dict[str, __DataField]
    pk : list[str]
    fields: list[str]
    table_name: str


@dataclass_transform()
class DataModel:
    """ Representing a database table """
    def __init__(self, **kwargs):
        self._saved_to_db = kwargs.get("saved_to_db", False)
        obj_attrs: dict[str, FieldValue] = {}
        self._deleted = False

        initial_fields = {k: v for k, v in kwargs.items() if k in self._MetaData.fields}
        for field in self._MetaData.fields:
            if field not in initial_fields:
                initial_fields.setdefault(field, None) # include every field even if not specified by kwargs

        for field_name, field_value in initial_fields.items():
            try: 
                if getattr(self._MetaData.class_attrs.get(field_name), "validate_value")(field_value):
                    value = field_value
            except Exception as e:
                raise e
            
            obj_attrs.setdefault(
                field_name, 
                FieldValue(
                    getattr(self._MetaData.class_attrs[field_name], "py_representation_type"),
                    value
                    )
                )
            
        self._obj_attrs = obj_attrs


    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._MetaData = MetaData()
        cls.DoesNotExist = DoesNotExist
        cls._MetaData.model_name = cls.__name__
        cls._MetaData.table_name = cls.__name__.lower()
        cls._MetaData.class_attrs = {k: v for k, v in cls.__dict__.items() if not k.startswith('_') and not issubclass(type(v), Exception)}
        
        cls._MetaData.fields = [k for k in cls._MetaData.class_attrs if not callable(cls._MetaData.class_attrs[k])]
        pks = [k for k in cls._MetaData.class_attrs if not callable(cls._MetaData.class_attrs[k]) and getattr(cls._MetaData.class_attrs[k], "primary_key", None)]
             
        if len(pks) == 1 and isinstance(cls._MetaData.class_attrs.get(pks[0]), IntDataField) and not getattr(cls._MetaData.class_attrs.get(pks[0]), "_explicit_auto_inc"):
            setattr(cls._MetaData.class_attrs.get(pks[0]), "auto_increment", True)
        if not len(pks):
            default_pk = "id"
            
            if default_pk in cls._MetaData.class_attrs:
                raise NoPrimaryKeyError("At least one primary key column must be specified and `id` field is declared as non primary key")
            
            pks.append(default_pk)
            cls._MetaData.fields.append(default_pk)
            cls._MetaData.class_attrs.setdefault(default_pk, IntDataField(primary_key = True, auto_increment = True))
            cls._MetaData.use_auto_id = True
        if len(pks) > 1:
            for pk in pks:
                field_desc_object = cls._MetaData.class_attrs.get(pk)
                if isinstance(field_desc_object, IntDataField):
                    field_desc_object.auto_increment = False
        cls._MetaData.pk = pks
        
        for field in cls._MetaData.fields:
            cls._MetaData.class_attrs[field].set_field_name(field)
        cls.manager = ModelManager(table_name=cls._MetaData.table_name, model = cls)


    @classmethod
    def migrate_model(cls, dry_run = False):

        sql_statement = f"CREATE TABLE IF NOT EXISTS {cls._MetaData.table_name}\n\t("\
        f"{",\n\t".join([cls._MetaData.class_attrs[field].column_sql for field in cls._MetaData.fields])}, " \
        f"PRIMARY KEY ({", ".join(cls._MetaData.pk)})" \
        f")"

        if dry_run:
            print(Text.yellow_text(sql_statement))
        else:
            db.execute(sql_statement)

    def _update_old_field_values(self, fields : list[str] | None = None):
        fields = fields if fields is not None else self._MetaData.pk
        for field in fields:
            field_value_object = self._obj_attrs[field]
            setattr(field_value_object, "old_value", getattr(field_value_object, "value"))

    @classmethod
    def __get_pk_lookup(cls):
        lookup_strings = [f"{pk} = :old_{pk}" for pk in cls._MetaData.pk]
        return " AND ".join(lookup_strings)



    def _save_object_to_db(self, db: Database, mode: str = "write", update_fields : list[str] | None = None):
        if mode == "write":
            fields_to_save = self._MetaData.fields 
            sql_statement = f"INSERT INTO {self._MetaData.table_name} ({", ".join(fields_to_save)}) VALUES (:{", :".join(fields_to_save)}) RETURNING *"
                    
        else:
            fields_to_save = update_fields if update_fields is not None else [field for field in self._get_modified_fields()]

            column_section = [f"{col} = :{col}" for col in fields_to_save]
            sql_statement = f"UPDATE {self._MetaData.table_name} SET {", ".join(column_section)} WHERE {self.__get_pk_lookup()} RETURNING *"
        
        values = {field : getattr(self._MetaData.class_attrs.get(field), "get_db_representation")(getattr(self._obj_attrs.get(field), "value")) for field in fields_to_save}
            
        if mode == "update":    
            values.update(self._get_old_pk_values())

        print(Text.yellow_text(sql_statement))
        print(Text.yellow_text(values))
        result = db.execute(sql_statement, values)
        self._saved_to_db = True
        return result

    
    def _update_field_values(self, updated_value_dict: dict[str, ]):
        for field, value in updated_value_dict.items():
            setattr(self, field, value)

    def _set_fields_modified(self, modified_value: bool =False):
        for field in self._MetaData.fields:
            setattr(self._obj_attrs[field], "_modified", modified_value)

    def save_object(self):
        if self._deleted:
            raise DeletedObjectError(f"Cannot save {self._MetaData.model_name}({self._MetaData.pk[0]}={self._obj_attrs.get(self._MetaData.pk[0]).value}) because it has been deleted.")
        if self._saved_to_db:
            if not self._get_modified_fields():
                return self
            result = self._save_object_to_db(db, mode="update")
            
        else:
            result = self._save_object_to_db(db)

        
        self._update_field_values(result[0])
        self._set_fields_modified(False)
        self._update_old_field_values()
        
        return self

    def _get_modified_fields(self):
        return {field: (v := getattr(self._obj_attrs[field], "value")) for field in self._MetaData.fields if getattr(self._obj_attrs[field], "_modified")}


    def _get_old_pk_values(self):
        return {f"old_{pk}": (v := getattr(self._obj_attrs[pk], "old_value") if getattr(self._obj_attrs[pk], "old_value") is not None else getattr(self._obj_attrs[pk], "value")) for pk in self._MetaData.pk}


    def __setattr__(self, name: str, value):
        if getattr(self, "_deleted", False):
            raise DeletedObjectError(f"Cannot save {self._MetaData.model_name}({self._MetaData.pk[0]}={self._obj_attrs.get(self._MetaData.pk[0]).value})")
        if name.startswith("_"):
            return super().__setattr__(name, value)
        if name not in self._MetaData.fields:
            raise InvalidFieldError(f"{name} is not a field on {self._MetaData.model_name}")
        field_value_object = self._obj_attrs[name]
        field_desc_object = self._MetaData.class_attrs[name]
        try:
            getattr(field_desc_object, "validate_value")(value)
        except Exception as e:
            raise InvalidFieldValueError(str(e))
        if getattr(field_desc_object, "primary_key") and not getattr(field_value_object, "_modified"): #if will be used in update lookup, and it hasn't already been modified
            self._update_old_field_values([name])
        setattr(field_value_object, "value", value)
        setattr(field_value_object, "_modified", True)

    def __getattribute__(self, name):
        if name in getattr(super().__getattribute__("_MetaData"), "fields"):
            return super().__getattribute__("_obj_attrs")[name]
        return super().__getattribute__(name)

    def delete_object(self):
        sql_statement = f"DELETE FROM {self._MetaData.table_name} WHERE {self.__get_pk_lookup()}"
        
        db.execute(sql_statement, self._get_old_pk_values())
        self._deleted = True

    @classmethod
    def _row_to_object(cls, row: dict):
        fields = {}
        for field in cls._MetaData.fields:
           fields.setdefault(field, cls._MetaData.class_attrs[field].get_py_representation(row.get(field, None)))
        obj = cls(saved_to_db = True, **fields) #initialize object with fields
        obj._set_fields_modified(False)
        
        return obj

    @classmethod
    def _gt(cls, field_name, field_value_name, field_value):
        return f"{field_name} > :{field_value_name}", {field_value_name: field_value}

    @classmethod
    def _gte(cls, field_name, field_value_name, field_value):
        return f"{field_name} >= :{field_value_name}", {field_value_name: field_value}

    @classmethod
    def _lt(cls, field_name, field_value_name, field_value):
        return f"{field_name} < :{field_value_name}", {field_value_name: field_value}

    @classmethod
    def _lte(cls, field_name, field_value_name, field_value):
        return f"{field_name} <= :{field_value_name}", {field_value_name: field_value}

    @classmethod
    def _contains(cls, field_name, field_value_name, field_value):
        return f"{field_name} LIKE :{field_value_name}", {field_value_name: f"%{field_value}%"}
    
    
    
    @classmethod
    def validate_lookup_args(cls, args: dict[str, ]):
        lookup_conditions = []
        for arg in args:
            operators = arg.split("__")
            key_field = operators.pop(0)

            if key_field not in cls._MetaData.fields:
                raise InvalidFieldError(f"{key_field} is not a field on {cls._MetaData.table_name}. The options are {cls._MetaData.fields}")
            if operators:
                operator_statement = getattr(cls, f"_{operators.pop(0)}")(key_field, arg, args.get(arg))
                lookup_conditions.append(operator_statement[0])
                args.update(operator_statement[1])
            else:
                lookup_conditions.append(f"{getattr(cls._MetaData.class_attrs[key_field], "field_name")} = :{arg}")
        return lookup_conditions

    @classmethod
    def _select_objects(cls, **kwargs):
        lookup_statement = ""
        if kwargs:
            try:
                lookup_conditions = cls.validate_lookup_args(kwargs)
                lookup_statement = f" WHERE {" AND ".join(lookup_conditions)}"
            except InvalidFieldError as e:
                print(Text.red_text("Invalid keys cannot be used in lookup"))
                raise e
        sql_statement = f"SELECT * FROM {cls._MetaData.table_name}{lookup_statement}"
        
        result = db.execute(sql_statement, kwargs)
        result = ResultSet([cls._row_to_object(row) for row in result], sql_statement, kwargs)

        return result

    

    def __str__(self):
        return f"{self._MetaData.model_name}({', '.join([field + '= \'' + str(self._obj_attrs[field]) + '\'' for field in self._MetaData.fields])})"
        
class ModelManager():
    def __init__(self, table_name: str, model: type[DataModel]):
        self.table_name: str = table_name   
        self.model = model
        
    def filter(self, **kwargs):
        return self.model._select_objects(**kwargs)

    def all(self):
        return self.model._select_objects()

    def get(self, **kwargs):
        result: ResultSet = self.model._select_objects(**kwargs)
        if not len(result):
            raise self.model.DoesNotExist("Object matching the query does not exist")
        if len(result) > 1:
            raise MultipleObjectsReturned(f"`{self.model._MetaData.model_name}.get` returned more than one object, it returned {len(result)}!")
        return result.data[0]

class ResultSet:
    "Holds results of a query"
    def __init__(self, data: list[DataModel], query: str, params: dict):
        self.query = query
        self.params = params
        self.data = data

    def __str__(self):
        return f"ResultSet Object {super().__str__()}"

    def __iter__(self):
        return ResultSetIterator(self.data)

    def __len__(self):
        return len(self.data)

class ResultSetIterator():
    def __init__(self, data: list[DataModel]):
        self.data = data
        self.current_index = 0

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            if self.current_index >= len(self.data):
                raise StopIteration
            item = self.data[self.current_index]
            self.current_index += 1
            return item
    
    

    
        

    

    