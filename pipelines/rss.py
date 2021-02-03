from dagster import pipeline, composite_solid, ModeDefinition
from solids.rss.main import (get_latest_entries,
    format_entries, update_entries, get_all_entries)
from solids.summarize.main import summarize_feeds
from solids.elastic.main import elastic_upsert
from solids.elastic.resource import es_resource
from solids.rss.resource import miniflux_rss

FEEDS = [
    'microsoft',
    'redhat',
    'ncsc',
    'f5',
    'cisa',
    'qualys'
]

@composite_solid
def composite_rss():
    unread_entries = get_latest_entries()
    unread_formatted = format_entries(unread_entries)
    historic_entries = get_all_entries()
    historic_formatted = format_entries(historic_entries)
    feed_summary = summarize_feeds(unread_formatted, historic_formatted)
    elastic_upsert(feed_summary)
    update_entries(unread_formatted)

@pipeline(
    mode_defs=[
        ModeDefinition(
            'prod', resource_defs={'rss': miniflux_rss, 'es': es_resource}
        )
    ]
)
def sync_new_rss():
    for feed in FEEDS:
       get_rss = composite_rss.alias(feed)
       get_rss()
