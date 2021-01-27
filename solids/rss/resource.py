from dagster import String, StringSource, resource
import miniflux

@resource(
    config_schema={
        'api_key': StringSource,
        'base_uri': String,
    }
)
def miniflux_rss(init_context):
    class MinifluxRss:
        def __init__(self, resource_config):
            self.api_key = resource_config['api_key']
            self.base_uri = resource_config['base_uri']
 
        @property
        def client(self):
            handler = miniflux.Client(self.base_uri,
                api_key=self.api_key)
            return handler

    return MinifluxRss(init_context.resource_config)