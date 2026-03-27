from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from pydantic import BaseModel, create_model, ConfigDict
import os
from pathlib import Path
import models as static_models
import database
from dynamic_models import DynamicModelFactory, Base
app = FastAPI(title='Configurab External LMS System', version='2.0.0',
    description='Dynamic schema-based mock LMS')
config_path = Path(__file__).parent / 'schema_config.json'
model_factory = DynamicModelFactory(str(config_path))
pydantic_models = {}


def create_pydantic_model(endpoint_name: str, endpoint_config: dict):
    """ Function: create_pydantic_model """
    fields_dict = {}
    create_fields_dict = {}
    for field in endpoint_config['fields']:
        field_name = field['name']
        field_type = field['type']
        python_type = {'Integer': int, 'String': str, 'Float': float,
            'Boolean': bool, 'DateTime': datetime, 'Date': date}.get(field_type
            , str)
        if field.get('required') and not field.get('auto_increment'):
            fields_dict[field_name] = python_type, ...
        else:
            fields_dict[field_name] = Optional[python_type], None
        if not field.get('auto_increment') and not field.get('primary_key'):
            if field.get('required'):
                create_fields_dict[field_name] = python_type, ...
            else:
                create_fields_dict[field_name] = Optional[python_type], None
    if 'joins' in endpoint_config:
        for join in endpoint_config['joins']:
            for field in join['fields']:
                f_name = field['name']
                f_type = field['type']
                py_type = {'Integer': int, 'String': str, 'Float': float,
                    'Boolean': bool}.get(f_type, str)
                fields_dict[f_name] = Optional[py_type], None
    out_model = create_model(f'{endpoint_name.title()}Out', **fields_dict,
        __config__=ConfigDict(from_attributes=True))
    create_model_pydantic = create_model(f'{endpoint_name.title()}Create',
        **create_fields_dict)
    return create_model_pydantic, out_model


def register_endpoint(endpoint_config: dict):
    """ Function: register_endpoint """
    endpoint_name = endpoint_config['name']
    path = endpoint_config['path']
    model_class = model_factory.get_model(endpoint_name)
    if not model_class:
        print(f'⚠ Model not found for endpoint: {endpoint_name}')
        return
    create_model_pydantic, out_model = create_pydantic_model(endpoint_name,
        endpoint_config)
    pydantic_models[endpoint_name] = {'create': create_model_pydantic,
        'out': out_model}

    @app.get(path, response_model=List[out_model], tags=[endpoint_name])
    async def get_endpoint_data(student_id: int, db: Session=Depends(
        database.get_db)):
        """Dynamically generated GET endpoint"""
        if 'joins' not in endpoint_config:
            records = db.query(model_class).filter(getattr(model_class,
                'student_id') == student_id).all()
            return records
        else:
            query = db.query(model_class)
            joined_tables = {}
            for join in endpoint_config['joins']:
                target_table_name = join['target_table']
                target_model = None
                if hasattr(static_models, 'Quiz'
                    ) and target_table_name == 'quizzes':
                    target_model = static_models.Quiz
                elif hasattr(static_models, 'Resource'
                    ) and target_table_name == 'resources':
                    target_model = static_models.Resource
                else:
                    pass
                if target_model:
                    on_field = getattr(model_class, join['on_field'])
                    target_key = getattr(target_model, join['target_key'])
                    query = query.join(target_model, on_field == target_key)
                    joined_tables[target_table_name] = target_model
            results = query.filter(getattr(model_class, 'student_id') ==
                student_id).all()
            enriched_records = []
            for record in results:
                rec_dict = {c.name: getattr(record, c.name) for c in record
                    .__table__.columns}
                for join in endpoint_config['joins']:
                    target_table_name = join['target_table']
                    target_model = None
                    if hasattr(static_models, 'Quiz'
                        ) and target_table_name == 'quizzes':
                        target_model = static_models.Quiz
                    elif hasattr(static_models, 'Resource'
                        ) and target_table_name == 'resources':
                        target_model = static_models.Resource
                    if not target_model:
                        continue
                    fk_val = getattr(record, join['on_field'])
                    target_key_field = getattr(target_model, join['target_key']
                        )
                    target_record = db.query(target_model).filter(
                        target_key_field == fk_val).first()
                    if target_record:
                        for field in join['fields']:
                            target_val = getattr(target_record, field['source']
                                )
                            rec_dict[field['name']] = target_val
                    else:
                        for field in join['fields']:
                            rec_dict[field['name']] = None
                enriched_records.append(rec_dict)
            return enriched_records

    @app.post(path, response_model=out_model, tags=[endpoint_name])
    async def create_endpoint_data(student_id: int, data:
        create_model_pydantic, db: Session=Depends(database.get_db)):
        """Dynamically generated POST endpoint"""
        data_dict = data.dict(exclude_unset=True)
        data_dict['student_id'] = student_id
        is_valid, error_msg = model_factory.validate_data(endpoint_name,
            data_dict)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        db_record = model_class(**data_dict)
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    print(f'  ✓ Registered endpoint: {path}')


@app.on_event('startup')
async def startup():
    """Initialize database and register dynamic endpoints"""
    print('\n🚀 Starting Configurable Sample-LMS...')
    static_models.Base.metadata.create_all(bind=database.engine)
    print('✓ Static models initialized')
    print('\n📦 Generating dynamic models...')
    model_factory.generate_all_models()
    Base.metadata.create_all(bind=database.engine)
    print('✓ Dynamic tables created')
    print('\n🔗 Registering dynamic endpoints...')
    for endpoint in model_factory.config.get('endpoints', []):
        register_endpoint(endpoint)
    print('\n✅ Sample-LMS ready!')


static_dir = Path(__file__).parent / 'static'
static_dir.mkdir(exist_ok=True)
app.mount('/static', StaticFiles(directory=str(static_dir)), name='static')


@app.get('/')
def read_root():
    """ Function: read_root """
    return {'message': 'Configurable Sample LMS', 'version': '2.0.0',
        'admin_ui': '/admin', 'schema_api': '/admin/schema'}


@app.get('/students', response_model=List[Dict])
def get_students(skip: int=0, limit: int=100, db: Session=Depends(database.
    get_db)):
    """ Function: get_students """
    students = db.query(static_models.Student).offset(skip).limit(limit).all()
    return [{'id': s.id, 'name': s.name} for s in students]


@app.get('/admin/schema')
def get_schema():
    """ Function: get_schema """
    return model_factory.config


@app.get('/admin/schema/endpoints')
def list_endpoints():
    """ Function: list_endpoints """
    return {'endpoints': [{'name': ep['name'], 'path': ep['path'],
        'description': ep.get('description', ''), 'field_count': len(ep[
        'fields'])} for ep in model_factory.config.get('endpoints', [])]}


@app.get('/admin/schema/endpoints/{endpoint_name}')
def get_endpoint_schema(endpoint_name: str):
    """ Function: get_endpoint_schema """
    endpoint = model_factory.get_endpoint_config(endpoint_name)
    if not endpoint:
        raise HTTPException(status_code=404, detail='Endpoint not found')
    return endpoint


class SchemaUpdate(BaseModel):
    """ Class: SchemaUpdate """
    config: dict


@app.put('/admin/schema')
async def update_schema(update: SchemaUpdate):
    """
    Update entire schema configuration.
    WARNING: This will reload all models and may cause data loss!
    """
    try:
        if 'endpoints' not in update.config:
            raise HTTPException(status_code=400, detail=
                "Missing 'endpoints' key")
        with open(config_path, 'w') as f:
            import json
            json.dump(update.config, f, indent=2)
        model_factory.reload_config()
        Base.metadata.create_all(bind=database.engine)
        return {'status': 'success', 'message':
            'Schema updated and reloaded', 'endpoint_count': len(update.
            config.get('endpoints', []))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class EndpointConfig(BaseModel):
    """ Class: EndpointConfig """
    name: str
    table_name: str
    path: str
    description: str = ''
    fields: List[Dict[str, Any]]


@app.post('/admin/schema/endpoints')
async def add_endpoint(endpoint: EndpointConfig):
    """Add a new endpoint to the schema"""
    if model_factory.get_endpoint_config(endpoint.name):
        raise HTTPException(status_code=400, detail='Endpoint already exists')
    model_factory.config['endpoints'].append(endpoint.dict())
    with open(config_path, 'w') as f:
        import json
        json.dump(model_factory.config, f, indent=2)
    model_factory.reload_config()
    model_factory.generate_all_models()
    Base.metadata.create_all(bind=database.engine)
    register_endpoint(endpoint.dict())
    return {'status': 'success', 'message':
        f"Endpoint '{endpoint.name}' added", 'path': endpoint.path}


@app.delete('/admin/schema/endpoints/{endpoint_name}')
async def delete_endpoint(endpoint_name: str):
    """Remove an endpoint from the schema"""
    endpoints = model_factory.config.get('endpoints', [])
    endpoint = next((ep for ep in endpoints if ep['name'] == endpoint_name),
        None)
    if not endpoint:
        raise HTTPException(status_code=404, detail='Endpoint not found')
    model_factory.config['endpoints'] = [ep for ep in endpoints if ep[
        'name'] != endpoint_name]
    with open(config_path, 'w') as f:
        import json
        json.dump(model_factory.config, f, indent=2)
    return {'status': 'success', 'message':
        f"Endpoint '{endpoint_name}' removed. Restart server to apply changes."
        }


@app.get('/admin')
def admin_ui():
    """ Function: admin_ui """
    admin_path = static_dir / 'admin' / 'index.html'
    if admin_path.exists():
        return FileResponse(admin_path)
    return {'message': 'Admin UI not yet implemented', 'api_docs': '/docs',
        'schema_api': '/admin/schema'}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8001, reload=False)
