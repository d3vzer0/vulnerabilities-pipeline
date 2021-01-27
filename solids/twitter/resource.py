from dagster import String, StringSource, resource
from .utils.api import Tweets

@resource(
    config_schema={
        'consumer_key': StringSource,
        'consumer_secret': StringSource
    }
)
def twitter_resource(init_context):
    class TwitterResource:
        def __init__(self, resource_config):
            self.consumer_key = resource_config['consumer_key']
            self.consumer_secret = resource_config['consumer_secret']

        @property
        def client(self):
            handler = Tweets(consumer_key=self.consumer_key,
                consumer_secret=self.consumer_secret)
            return handler

    return TwitterResource(init_context.resource_config)