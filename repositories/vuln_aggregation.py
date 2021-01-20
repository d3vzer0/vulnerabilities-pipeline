
from dagster import repository
from nvd.nvd_pipeline import sync_new_cves
from twitter.twitter_pipeline import sync_new_tweets
from rss.miniflux_pipeline import sync_new_rss

@repository
def vuln_aggregation_repo():
    return {
        'pipelines': {
            "sync_new_cves": lambda: sync_new_cves,
            'sync_new_tweets': lambda: sync_new_tweets,
            'sync_new_rss': lambda: sync_new_rss
        }
    }