from dagster import String, StringSource, resource
from elasticsearch import Elasticsearch, helpers

@resource(
    config_schema={
        'uri': StringSource,
    }
)
def es_resource(init_context):
    class ESResource:
        def __init__(self, resource_config):
            self.uri = resource_config['uri']
 
        @property
        def client(self):
            handler = Elasticsearch([self.uri])
            return handler

    return ESResource(init_context.resource_config)