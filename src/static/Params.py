from enum import Enum


class HandlerParams(Enum):
    SEARCH_URL = 'https://www.pathofexile.com/api/trade/search/'
    EXCHANGE_URL = 'https://www.pathofexile.com/api/trade/exchange/'
    FETCH_URL = 'https://www.pathofexile.com/api/trade/fetch/'
    STASH_URL = 'http://api.pathofexile.com/public-stash-tabs'
    MAXIMUM_BATCH_SIZE = 10
    MAXIMUM_FETCH_SIZE = 200


class NegotiatorParams(Enum):
    SLEEP_TIMER = 1


class AWSParams(Enum):
    DYNAMO_ENDPOINT_URL = 'https://dynamodb.us-east-1.amazonaws.com'
    # TODO: Create a function to compose the URL instead of using
    # a static value
