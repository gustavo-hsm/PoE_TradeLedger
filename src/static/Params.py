from enum import Enum


class HandlerParams(Enum):
    SEARCH_URL = 'https://www.pathofexile.com/api/trade/search/'
    EXCHANGE_URL = 'https://www.pathofexile.com/api/trade/exchange/'
    FETCH_URL = 'https://www.pathofexile.com/api/trade/fetch/'
    MAXIMUM_BATCH_SIZE = 10
    MAXIMUM_FETCH_SIZE = 200


class NegotiatorParams(Enum):
    SLEEP_TIMER = 1
