import requests
import json

from itertools import repeat
from datetime import datetime
from time import sleep


class RequestHandler():

    def __init__(self, league='standard'):
        self.league = league
        self.trade_url = "https://www.pathofexile.com/api/trade/"
        self.request_indexer = []
        self.batch_size = 10
        self.trade_url_exchange = self.trade_url + "exchange/" + self.league
        self.trade_url_search = self.trade_url + "search/" + self.league
        self.trade_url_fetch = self.trade_url + "fetch/"

    def query_api(self, api, json_header):
        '''
        Handles user request through the API

        api: String 'exchange' or 'search' - Whether to browse for
        Currencies (exchange) or Items (search)

        json_header: JSON formatted data to request
        '''

        # Which API to request, defaults to 'search'
        request_url = {
            'exchange': self.trade_url_exchange,
            'search': self.trade_url_search
        }.get(api, 'exchange')

        # Request/Response
        response = requests.post(request_url, json=json_header)

        # Check if something went wrong
        if response.status_code != 200:
            self._api_error_handler(response)

        # Request was successful. We should receive a JSON response
        # with keys 'id', 'complexity' and 'result'.
        #
        # id: The Query ID to request data
        # complexity: Unknown. So far only returned 'null'
        # result: List of results matching the query request
        payload = json.loads(response.text)
        query_id = payload['id']
        query_complexity = payload['complexity']
        query_result = payload['result']
        print('Found %s offers' % len(query_result))

        # We need to index our search if results are larger than batch size
        while len(query_result) > self.batch_size:
            self.request_indexer.append([query_result.pop(i)
                                        for i in repeat(0, self.batch_size)])

        # Append remaining results smaller than batch size
        if len(query_result) > 0:
            self.request_indexer.append(query_result)

        results = []
        # Indexer is done, now we start querying the actual data
        for index in self.request_indexer:
            items = ','.join(index)
            query = f"{self.trade_url_fetch}{items}?query={query_id}"
            api_response = requests.get(query)
            response_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

            # Check if something went wrong
            if api_response.status_code != 200:
                self._api_error_handler(api_response)

            # Request was successful. Now we can properly structure
            # the response and collect useful data
            for item in json.loads(api_response.text)['result']:
                results.append({
                    'offer_id': item['id'],
                    'trade_league': item['item']['league'],
                    'buying_currency': item['listing']['price']['currency'],
                    'buying_price': item['listing']['price']['amount'],
                    'offer_currency': item['item']['typeLine'],
                    'offer_amount': 1,
                    'offer_total_stock': item['item']['stackSize'],
                    'acc_user': item['listing']['account']['name'],
                    'acc_user_online': item['listing']
                    ['account']['online'] is not None,
                    'indexed_time': item['listing']['indexed'],
                    'processed_time': response_time,
                })

            # Wait 1 second before requesting the API again
            sleep(1)

        return results

    def _api_error_handler(self, response):
        # TODO Handle HTTP errors properly, especially HTTP 429
        raise Exception('Something went wrong...\nHTTP %s\n%s' %
                        (response.status_code, response.text))

        # HTTP Errors
        #
        # 200 OK
        # 400 Bad Request
        # 404 Not Found
        # 429 Too Many Requests
        # 500 Server Error

        # HTTP 400 API Errors
        #
        # 1   Resource not Found
        # 2   Invalid query
        # 3   Rate limit exceeded
        # 4   Internal error
        # 5   Unexpected content type
        # 6   Forbidden
        # 7   Temporarily Unavailable
        # 8   Unauthorized
        # 9   Method not allowed
        # 10  Unprocessable Entity
