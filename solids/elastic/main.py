from dagster import solid, Field, Dict, String, List
from elasticsearch import Elasticsearch, helpers

@solid(
    config_schema={
        'index': Field(
            String,
            is_required=False,
            default_value='applications-streamio',
            description='Name of index'
        ),
        'uri': Field(
            String,
            is_required=True,
            description='URI of ES node'
        )
    }
)
def elastic_upsert(context, data: List[Dict]):
    es = Elasticsearch([context.solid_config['uri']])
    context.log.info(f'Saving {len(data)} documents to {context.solid_config["index"]}')
    documents = [{**doc, '_index': context.solid_config['index'], '_id': doc['fingerprint']}
        for doc in data]
    helpers.bulk(es, documents, chunk_size=1000)
