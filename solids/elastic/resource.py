from dagster import String, StringSource, resource
from elasticsearch import Elasticsearch, helpers
from ssl import create_default_context

@resource(
    config_schema={
        'uri': StringSource,
        'ca_path': StringSource,
    }
)
def es_resource(init_context):
    class ESResource:
        def __init__(self, resource_config):
            self.uri = resource_config['uri']
            self.ca_path = resource_config['ca_path']
 
        @property
        def client(self):
            context = create_default_context(cafile=self.ca_path)
            handler = Elasticsearch([self.uri], ssl_context=context)
            return handler

    return ESResource(init_context.resource_config)