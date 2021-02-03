
from dagster import repository, ScheduleDefinition
from pipelines.nvd import sync_new_cves
from pipelines.twitter import sync_new_tweets
from pipelines.rss import sync_new_rss
from yaml import load
from yaml import CLoader as Loader


def load_preset(path):
    with open(path, 'r') as preset:
        data = load(preset.read(), Loader=Loader)
        return data


def schedules():
    return [
        ScheduleDefinition(
            name='rss_schedule',
            cron_schedule='*/20 * * * *',
            pipeline_name='sync_new_rss',
            run_config=load_preset('pipelines/presets/prod_rss.yaml'),
            mode='prod'
        ),
        ScheduleDefinition(
            name='twitter_schedule',
            cron_schedule='*/20 * * * *',
            pipeline_name='sync_new_tweets',
            run_config=load_preset('pipelines/presets/prod_twitter.yaml'),
            mode='prod'
        ),
        ScheduleDefinition(
            name='nvd_schedule',
            cron_schedule='*/30 * * * *',
            pipeline_name='sync_new_cves',
            run_config=load_preset('pipelines/presets/prod_nvd.yaml'),
            mode='prod'

        )
    ]

@repository
def vuln_aggregation_repo():
    return [sync_new_cves, sync_new_tweets, sync_new_rss] + schedules()
