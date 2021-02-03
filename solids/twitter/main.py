from dagster import solid, Field, Int, Dict, String, OutputDefinition, List, Output
from .utils.transforms import Transform
from .utils.matching import Match
import redis

@solid(
    required_resource_keys={'twitter'},
    output_defs=[OutputDefinition(List[Dict], 'tweets', is_required=False)],
    config_schema={
        'init_limit': Field(
            Int,
            is_required=False,
            default_value=500,
            description='Max tweets on first run'
        ),
        'query': Field(
            String,
            is_required=False,
            default_value='CVE-',
            description='Twitter Search Query'
        )
    }
)
def get_latest_tweets(context) -> List[Dict]:
    ''' Get the latest tweets from the Twitter API '''
    client = context.resources.twitter.client
    get_tweets = client.query(context.solid_config['query'], since=None)
    context.log.info(f'Parsing tweets for {len(get_tweets)} entries')
    parsed_tweets = [Transform(tweet).to_dict for tweet in get_tweets]
    if parsed_tweets: yield Output(parsed_tweets, output_name='tweets')


@solid(
    config_schema={
        'patterns': Field(
            [str],
            is_required=False,
            default_value=['cve'],
            description='List of patterns to use'
        )
    }
)
def extract_content(context, tweets:List[Dict]) -> List[Dict]:
    ''' Extract common elements like CVE ID from tweet '''
    context.log.info(f'Parsing tweets for {len(tweets)} entries')
    all_tweets = []
    for tweet in tweets:
        match_tweet = Match(tweet['tweet.content'])
        match_tweet.from_regex(pattern_selection=context.solid_config['patterns'])
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
