from dagster import solid, Field, Dict, String, List
from elasticsearch import helpers

@solid(
    config_schema={
        'index': Field(
            String,
            is_required=False,
            default_value='applications-streamio',
            description='Name of index'
        )
    }
)
def elastic_upsert(context, data: List[Dict]):
    es = context.resources.es.client
    context.log.info(f'Saving {len(data)} documents to {context.solid_config["index"]}')
    documents = [{**doc, '_index': context.solid_config['index'], '_id': doc['fingerprint']}
        for doc in data]
    helpers.bulk(es, documents, chunk_size=1000)
