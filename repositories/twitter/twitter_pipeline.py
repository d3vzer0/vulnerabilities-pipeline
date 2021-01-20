from .utils.api import Tweets
from .utils.transforms import Transform
from .utils.matching import Match
from dagster import pipeline, solid, Field, Int, Dict, String, List, Optional
from elastic.elastic_pipeline import elastic_upsert
import redis

@solid(
    config_schema={
        'consumer_key': Field(
            String,
            is_required=True,
            description='API consumer key'
        ),
        'consumer_secret': Field(
            String,
            is_required=True,
            description='API consumer secret'
        ),
        'init_limit': Field(
            Int,
            is_required=False,
            default_value=500,
            description='Max tweets on first run'
        )
    }
)
def get_latest_tweets(context, offset: Optional[String]) -> List[Dict]:
    ''' Get the latest tweets from the Twitter API '''
    tweet_object = Tweets(consumer_key=context.solid_config['consumer_key'],
        consumer_secret=context.solid_config['consumer_secret'])
    get_tweets = tweet_object.query('CVE-', since=offset)
    context.log.info(f'Parsing tweets for {len(get_tweets)} entries')
    parsed_tweets = [Transform(tweet).to_dict for tweet in get_tweets]
    context.log.info(f'Sample - {parsed_tweets[0]}')
    return parsed_tweets

@solid
def extract_content(context, tweets:List[Dict]) -> List[Dict]:
    ''' Extract common elements like CVE ID from tweet '''
    context.log.info(f'Parsing tweets for {len(tweets)} entries')
    all_tweets = []
    for tweet in tweets:
        match_tweet = Match(tweet['tweet.content'])
        match_tweet.from_regex(pattern_selection=['cve'])
        tweet_data = { **tweet, **match_tweet.denormalized, 'regex.extract': True if match_tweet else False }
        tweet_data['tags'] = tweet_data['tweet.tags'] + tweet_data.get('tags', [])
        all_tweets.append(tweet_data)
    return all_tweets


@solid(
    config_schema={
        'key': Field(
            String,
            is_required=True,
            description='Default key to get offset'
        ),
        'password': Field(
            String,
            is_required=False,
            description='Redis password'
        ),
        'host': Field(
            String,
            is_required=False,
            default_value='localhost',
            description='Redis host'
        ),
        'port': Field(
            Int,
            is_required=False,
            default_value=6379,
            description='Redis port'
        ),
        'db': Field(
            Int,
            is_required=False,
            default_value=0,
            description='Redis DB'
        )
    }
)
def get_offset(context):
    r = redis.Redis(host=context.solid_config['host'],
        port=context.solid_config['port'], db=context.solid_config['db'],
        password=context.solid_config['password'])
    return r.get(context.solid_config['key'])

@pipeline
def sync_new_tweets():
    latest_offset = get_offset()
    new_tweets = get_latest_tweets(latest_offset)
    extract_items = extract_content(new_tweets)
    elastic_upsert(extract_items)
