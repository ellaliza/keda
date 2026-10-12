from dataclasses import dataclass
from typing import dataclass_transform
from exceptions import NoPrimaryKeyError, InvalidFieldValueError
from database_wrapper import Database
from fields import FieldValue


@dataclass_transform()
class DataModel:
    """ Representing a database table """
    def __init__(self, **kwargs):
        self._saved_to_db = kwargs.get("saved_to_db", False)
        obj_attrs = {}

        for field_name in self.MetaData.fields:
            obj_attrs.setdefault(field_name, FieldValue(getattr(self.MetaData.class_attrs[field_name], "py_representation_type")))

        for field_name, field_value in {k: v for k, v in kwargs.items() if k in self.MetaData.fields}.items():
            #implementation 1: set on actual object, field object still lives in MetaData.class_attr
            #setattr(self, field_name, field_value) #keep DataField as a "schema" or guide on how columns behave, etc.

            #implementation #2: set value on field object - wrong i think. would mean one field object for the whole class
            #setattr(self.MetaData.class_attrs[field_name], "value", field_value)

            #implementation #3: (added a FieldValue to the DataField class) set value on fieldValue object 
            setattr(obj_attrs[field_name], "value", field_value)
        self._obj_attrs = obj_attrs


    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        #dataclass(cls, kw_only=True, init)
        cls.MetaData.model_name = cls.__name__
        cls.MetaData.table_name = cls.__name__.lower()
        cls.MetaData.class_attrs = {k: v for k, v in cls.__dict__.items() if not k.startswith('_')}
        pks = [k for k in cls.MetaData.class_attrs if not callable(cls.MetaData.class_attrs[k]) and cls.MetaData.class_attrs[k].primary_key]
        cls.MetaData.fields = [k for k in cls.MetaData.class_attrs if not callable(cls.MetaData.class_attrs[k])]
        if not len(pks):
            if "id" in cls.MetaData.class_attrs:
                raise NoPrimaryKeyError("At least one primary key column must be specified and `id` field is declared as non primary key")

            cls.MetaData.use_auto_id = True
        cls.MetaData.pk = pks
        cls.MetaData.fields = [k for k in cls.__dict__.keys() if not k.startswith("_") and not callable(cls.MetaData.class_attrs[k])]
        for field in cls.MetaData.fields:
            cls.MetaData.class_attrs[field].set_field_name(field)


    class MetaData:
        use_auto_id = False
        model_name: str
        class_attrs : dict
        pk : list[str]
        fields: list[str]
        table_name: str
        pass



    @classmethod
    def migrate_model(cls, db: Database, dry_run = False):

        sql_statement = f"CREATE TABLE IF NOT EXISTS {cls.MetaData.table_name} \n\t("\
        f"{", \n\t".join([cls.MetaData.class_attrs[field].column_sql for field in cls.MetaData.fields])}" \
        f")"

        if dry_run:
            print(sql_statement)
        else:
            db.execute(sql_statement)

    def _update_old_field_values(self, fields : list[str] | None = None):
        fields = fields if fields is not None else self.MetaData.pk
        for field in fields:
            field_value_object = self._obj_attrs[field]
            setattr(field_value_object, "old_value", getattr(field_value_object, "value"))

    @classmethod
    def __get_pk_lookup(cls):
        lookup_strings = [f"{pk} = :old_{pk}" for pk in cls.MetaData.pk]
        return " AND ".join(lookup_strings)



    def _save_object_to_db(self, db: Database, mode: str = "write", update_fields : list[str] | None = None):
        if mode == "write":
            fields_to_save = self.MetaData.fields 
            sql_statement = f"INSERT INTO {self.MetaData.table_name} ({", ".join(fields_to_save)}) VALUES (:{", :".join(fields_to_save)})"
                    
        else:
            fields_to_save = update_fields if update_fields is not None else [field for field in self._get_modified_fields()]
            column_section = [f"{col} = :{col}" for col in fields_to_save]
            sql_statement = f"UPDATE {self.MetaData.table_name} SET {", ".join(column_section)} WHERE {self.__get_pk_lookup()}"
        
        values = {field : getattr(self._obj_attrs.get(field), "py_representation")() for field in fields_to_save}
            
        if mode == "update":    
            values.update(self._get_old_pk_values())

        print(values)
        print(sql_statement)
        result = db.execute(sql_statement, values)
        self._saved_to_db = True
        return result

    @classmethod
    def update_objects(cls, **kwargs: dict):
        pass

    def _set_fields_modified(self, modified_value: bool =False):
        for field in self.MetaData.fields:
            setattr(self._obj_attrs[field], "_modified", modified_value)

    def save_object(self, db: Database):
        if self._saved_to_db:
            result = self._save_object_to_db(db, mode="update")
            
        else:
            result = self._save_object_to_db(db)
            if len(self.MetaData.pk) == 1 and not any([self._obj_attrs[pk].value for pk in self.MetaData.pk]):
                print("Refreshing object pks")
                setattr(self._obj_attrs[self.MetaData.pk[0]], "value", result.lastrowid)
        self._set_fields_modified(False)
        self._update_old_field_values()
        return result

    def _get_modified_fields(self):
        return {field: (v := getattr(self._obj_attrs[field], "value")) for field in self.MetaData.fields if getattr(self._obj_attrs[field], "_modified")}
 

    def _get_old_pk_values(self):
        return {f"old_{pk}": (v := getattr(self._obj_attrs[pk], "old_value") if getattr(self._obj_attrs[pk], "old_value") is not None else getattr(self._obj_attrs[pk], "value")) for pk in self.MetaData.pk}


    def __setattr__(self, name: str, value):
        if name.startswith("_"):
            return super().__setattr__(name, value)
        if name not in self.MetaData.fields:
            raise InvalidFieldValueError(f"{name} is not a field on {self.MetaData.model_name}")
        field_value_object = self._obj_attrs[name]
        field_desc_object = self.MetaData.class_attrs[name]
        if getattr(field_desc_object, "primary_key") and not getattr(field_value_object, "_modified"): #if will be used in update lookup, and it hasn't already been modified
            self._update_old_field_values([name])
        setattr(field_value_object, "value", value)
        setattr(field_value_object, "_modified", True)

    def __getattribute__(self, name):
        if name in getattr(super().__getattribute__("MetaData"), "fields"):
            return super().__getattribute__("_obj_attrs")[name]
        return super().__getattribute__(name)

    def delete_object(self, db: Database):
        sql_statement = f"DELETE FROM {self.MetaData.table_name} WHERE {self.__get_pk_lookup()}"
        print(sql_statement)
        return db.execute(sql_statement, self._get_old_pk_values())

    @classmethod
    def _row_to_object(cls, row: dict):
        obj = cls(saved_to_db = True) #initialize object
        obj._set_fields_modified(False)
        for field in cls.MetaData.fields:
            setattr(obj, field, cls.MetaData.class_attrs[field].py_representation_type(row.get(field, None)))
        return obj


    @classmethod
    def select_objects(cls, db):
        sql_statement = f"SELECT * FROM {cls.MetaData.table_name}"
        result = db.execute(sql_statement).fetchall()
        result = [cls._row_to_object(row) for row in result]
        return result

    def __str__(self):
        return f"{self.MetaData.model_name}({', '.join([field + '=' + str(self._obj_attrs[field]) for field in self.MetaData.fields])})"
        
        