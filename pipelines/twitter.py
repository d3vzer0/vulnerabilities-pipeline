from dagster import pipeline, ModeDefinition, PresetDefinition
from dagster.utils import file_relative_path
from solids.twitter.main import (get_latest_tweets,
    extract_content, get_offset)
from solids.elastic.main import elastic_upsert
from solids.elastic.resource import es_resource
from solids.twitter.resource import twitter_resource


@pipeline(
    mode_defs=[
        ModeDefinition(
            'prod', resource_defs={'twitter': twitter_resource, 'es': es_resource}
        )
    ],
    preset_defs=[
        PresetDefinition.from_files(
            'prod',
            config_files=[
                file_relative_path(__file__, 'presets/prod_twitter.yaml')
            ],
            mode='prod',
        ),
    ]
)
def sync_new_tweets():
    # latest_offset = get_offset()
    new_tweets = get_latest_tweets()
    extract_items = extract_content(new_tweets)
    elastic_upsert(extract_items)
