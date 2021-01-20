from .utils.transforms import Transform
from dagster import pipeline, solid, Field, Int, Dict, String, List
from elastic.elastic_pipeline import elastic_upsert
import miniflux

@solid(
    config_schema={
        'api_key': Field(
            String,
            is_required=True,
            description='API consumer key'
        ),
        'uri': Field(
            String,
            is_required=True,
            description='API consumer secret'
        ),
        'feed': Field(
            Int,
            is_required=True,
        )
    }
)
def get_latest_entries(context) -> List[Dict]:
    ''' Get the latest RSS entries'''
    client = miniflux.Client(context.solid_config['uri'], api_key=context.solid_config['api_key'])
    entries = client.get_feed_entries(context.solid_config['feed'], status='unread').get('entries', [])
    context.log.info(f'Received {len(entries)} entries')
    return entries


@solid
def format_entries(context, entries:List[Dict]) -> List[Dict]:
    ''' Format to ECS Schema '''
    context.log.info(f'Parsing {len(entries)} total')
    entries_modified = [Transform(entry).to_dict for entry in entries]
    context.log.info(f'Sample - {entries_modified[0]}')
    return entries_modified

@solid(
    config_schema={
        'api_key': Field(
            String,
            is_required=True,
            description='API consumer key'
        ),
        'uri': Field(
            String,
            is_required=True,
            description='URI'
        )
    }
)
def update_entries(context, entries:List[Dict]):
    ''' Mark entries as read '''
    client = miniflux.Client(context.solid_config['uri'], api_key=context.solid_config['api_key'])
    entries_id = [entry['rss.id'] for entry in entries]
    client.update_entries(entries_id, 'read')


@pipeline
def sync_new_rss():
    entries = get_latest_entries()
    formatted = format_entries(entries)
    elastic_upsert(formatted)
    update_entries(formatted)

