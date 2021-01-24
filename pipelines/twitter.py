from dagster import pipeline
from solids.twitter.main import (get_latest_tweets,
    extract_content, get_offset)
from solids.elastic.main import elastic_upsert

@pipeline
def sync_new_tweets():
    # latest_offset = get_offset()
    new_tweets = get_latest_tweets()
    extract_items = extract_content(new_tweets)
    elastic_upsert(extract_items)
