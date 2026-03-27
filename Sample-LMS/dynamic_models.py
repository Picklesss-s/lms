from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json
from pathlib import Path
from datetime import datetime, date
try:
    from models import Base
except ImportError:
    Base = declarative_base()
TYPE_MAPPING = {'Integer': Integer, 'String': String, 'Float': Float,
    'Boolean': Boolean, 'DateTime': DateTime, 'Date': Date}


class DynamicModelFactory:
    """ Class: DynamicModelFactory """

    def __init__(self, config_path: str):
        """ Function: __init__ """
        self.config_path = Path(config_path)
        self.config = None
        self.models = {}
        self.load_config()

    def load_config(self):
        """ Function: load_config """
        with open(self.config_path, 'r') as f:
            self.config = json.load(f)
        print(
            f"✓ Loaded schema config: {self.config.get('lms_name', 'Unknown')}"
            )

    def reload_config(self):
        """ Function: reload_config """
        self.load_config()
        self.models = {}
        self.generate_all_models()
        print('✓ Schema reloaded and models regenerated')

    def create_model_from_endpoint(self, endpoint_config: dict):
        """ Function: create_model_from_endpoint """
        table_name = endpoint_config['table_name']
        fields = endpoint_config['fields']
        attrs = {'__tablename__': table_name, '__table_args__': {
            'extend_existing': True}}
        for field in fields:
            field_name = field['name']
            field_type = field['type']
            column_type = TYPE_MAPPING.get(field_type, String)
            column_args = []
            column_kwargs = {}
            if field.get('primary_key'):
                column_kwargs['primary_key'] = True
            if field.get('auto_increment'):
                column_kwargs['autoincrement'] = True
            if field.get('required') and not field.get('primary_key'):
                column_kwargs['nullable'] = False
            if field.get('foreign_key'):
                fk_table, fk_column = field['foreign_key'].split('.')
                column_args.append(ForeignKey(f'{fk_table}.{fk_column}'))
            attrs[field_name] = Column(column_type, *column_args, **
                column_kwargs)
        model_class = type('Dynamic' + endpoint_config['name'].title().
            replace('_', ''), (Base,), attrs)
        return model_class

    def generate_all_models(self):
        """ Function: generate_all_models """
        for endpoint in self.config.get('endpoints', []):
            model_name = endpoint['name']
            model_class = self.create_model_from_endpoint(endpoint)
            self.models[model_name] = model_class
            print(
                f"  ✓ Generated model: {model_class.__name__} -> {endpoint['table_name']}"
                )
        return self.models

    def get_model(self, endpoint_name: str):
        """ Function: get_model """
        return self.models.get(endpoint_name)

    def get_all_models(self):
        """ Function: get_all_models """
        return self.models

    def get_endpoint_config(self, endpoint_name: str):
        """ Function: get_endpoint_config """
        for endpoint in self.config.get('endpoints', []):
            if endpoint['name'] == endpoint_name:
                return endpoint
        return None

    def validate_data(self, endpoint_name: str, data: dict) ->tuple[bool, str]:
        """ Function: validate_data """
        endpoint = self.get_endpoint_config(endpoint_name)
        if not endpoint:
            return False, f'Unknown endpoint: {endpoint_name}'
        for field in endpoint['fields']:
            if field.get('required') and not field.get('auto_increment'):
                if field['name'] not in data:
                    return False, f"Missing required field: {field['name']}"
        for field_name, value in data.items():
            field_def = next((f for f in endpoint['fields'] if f['name'] ==
                field_name), None)
            if not field_def:
                continue
            expected_type = field_def['type']
            if expected_type == 'Integer' and not isinstance(value, int):
                return False, f"Field '{field_name}' must be an integer"
            elif expected_type == 'Float' and not isinstance(value, (int,
                float)):
                return False, f"Field '{field_name}' must be a number"
            elif expected_type == 'Boolean' and not isinstance(value, bool):
                return False, f"Field '{field_name}' must be a boolean"
            if 'min' in field_def and value < field_def['min']:
                return (False,
                    f"Field '{field_name}' below minimum: {field_def['min']}")
            if 'max' in field_def and value > field_def['max']:
                return (False,
                    f"Field '{field_name}' above maximum: {field_def['max']}")
        return True, ''


model_factory = None
