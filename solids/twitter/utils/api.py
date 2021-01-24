import tweepy

class Tweets:
    def __init__(self, consumer_key=None, consumer_secret=None):
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True)

    def query(self, query, since=None, result_type='recent'):
        return [tweet for tweet in \
            tweepy.Cursor(self.api.search, q=query, since_id=since,
            count=1000, tweet_mode='extended').items(2000)]
