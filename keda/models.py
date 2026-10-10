from dataclasses import dataclass
from typing import dataclass_transform
from exceptions import NoPrimaryKeyError
from database_wrapper import Database

@dataclass_transform()
class DataModel:
    """ Representing a database table """
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        dataclass(cls, kw_only=True)
        cls.MetaData.model_name = cls.__name__
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
        pass

    @classmethod
    def migrate_model(cls, db: Database, dry_run = False):

        sql_statement = f"CREATE TABLE IF NOT EXISTS {cls.MetaData.model_name.lower()} \n\t("\
        f"{", \n\t".join([cls.MetaData.class_attrs[field].column_sql for field in cls.MetaData.fields])}" \
        f")"

        if dry_run:
            print(sql_statement)
        else:
            db.execute(sql_statement)