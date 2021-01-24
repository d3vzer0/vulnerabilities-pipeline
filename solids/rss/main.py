from .utils.transforms import Transform
from dagster import solid, Field, Int, Dict, String, List
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
        )
    }
)
def get_latest_entries(context, feed: Int) -> List[Dict]:
    ''' Get the latest RSS entries'''
    client = miniflux.Client(context.solid_config['uri'], api_key=context.solid_config['api_key'])
    entries = client.get_feed_entries(feed, status='unread').get('entries', [])
    context.log.info(f'Received {len(entries)} entries')
    return entries


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
        )
    }
)
def get_all_entries(context, feed: Int) -> List[Dict]:
    ''' Get the latest RSS entries'''
    client = miniflux.Client(context.solid_config['uri'], api_key=context.solid_config['api_key'])
    entries = client.get_feed_entries(feed).get('entries', [])
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
        ),
        'state': Field(
            String,
            is_required=False,
            default_value='read',
            description='state'  
        )
    }
)
def update_entries(context, entries:List[Dict]):
    ''' Mark entries as read '''
    client = miniflux.Client(context.solid_config['uri'], api_key=context.solid_config['api_key'])
    entries_id = [entry['rss.id'] for entry in entries]
    client.update_entries(entries_id, context.solid_config['state'])
