from dagster import pipeline, composite_solid, Int
from solids.rss.main import (get_latest_entries,
    format_entries, update_entries, get_all_entries)
from solids.summarize.main import summarize_feeds
from solids.elastic.main import elastic_upsert


FEEDS = [
    'microsoft',
    'redhat',
    'ncsc',
    'f5',
    'cisa'
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

@pipeline
def sync_new_rss():
    for feed in FEEDS:
       get_rss = composite_rss.alias(feed)
       get_rss()
