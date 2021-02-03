from .utils.transforms import Transform
from dagster import solid, Field, Int, Dict, String, List


@solid(required_resource_keys={'rss'})
def get_latest_entries(context, feed: Int) -> List[Dict]:
    ''' Get the latest RSS entries'''
    client = context.resources.rss.client
    entries = client.get_feed_entries(feed, status='unread').get('entries', [])
    context.log.info(f'Received {len(entries)} entries')
    return entries


@solid(required_resource_keys={'rss'})
def get_all_entries(context, feed: Int) -> List[Dict]:
    ''' Get the latest RSS entries'''
    client = context.resources.rss.client
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
    required_resource_keys={'rss'},
    config_schema={
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
    client = context.resources.rss.client
    entries_id = [entry['rss.id'] for entry in entries]
    client.update_entries(entries_id, context.solid_config['state'])
