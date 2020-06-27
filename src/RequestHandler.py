import requests
import sys
import json
from time import sleep
from datetime import datetime

from Observer import Publisher, Subscriber
import ExchangeParser as ep


class RequestHandler():
    def __init__(self, ExchangeItem, league):
        self.ExchangeItem = ExchangeItem
        self.league = league
        self.trade_url = "https://www.pathofexile.com/api/trade/"
        self.trade_url_exchange = self.trade_url + "exchange/" + self.league
        self.trade_url_search = self.trade_url + "search/" + self.league
        self.trade_url_fetch = self.trade_url + "fetch/"
        self.retry = True

    def require(self, parameter_list):
        raise NotImplementedError

    def send_request(self):
        while self.retry:
            self.require()

    def handle_status_code(self, status_code):
        print(status_code)
        if status_code >= 500:
            # Server side error:  Bad Gateway, Cloudfare DDoS Protection, etc
            # Wait a few minutes before trying again
            self._generate_error_log(status_code)
            self._try_again_later(180)

        elif status_code >= 400:
            # Client side error: Something went wrong with our request
            self._generate_error_log(status_code)
            if status_code in [405, 429]:
                # Codes 405 (Method not Allowed) and 429 (Too Many Requests)
                # I noticed 405 being thrown when the servers went offline
                # for maintenance. Both of these codes will be handled
                # similarly: Timeout and try again later
                self._try_again_later(30)
            else:
                # Remaining codes: 400 (Bad Request) and 404 (Not Found)
                # Request cannot be fulfilled. No point in trying again
                self.retry = False

                # HTTP 400 code reference
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
        elif status_code >= 300:
            # Request was redirected
            self._generate_error_log(status_code)
            self.retry = False
        else:
            # 2xx: Request was successful
            self.retry = False

    def _try_again_later(self, seconds=30):
        self.retry = True
        sleep(seconds)

    def _generate_error_log(self, status_code):
        # TODO: Implement proper logging
        print('Something went wrong...\nHTTP %s' % status_code)
        sys.stdout.flush()


class PostHandler(RequestHandler, Publisher):
    def __init__(self, ExchangeItem, league):
        super().__init__(ExchangeItem, league)
        self.subscribers = set()
        self.subscribers_response = {
            'id': None,
            'complexity': None,
            'result': None,
        }

    def publish(self):
        super().publish()

    def subscribe(self, subscriber):
        super().subscribe(subscriber)

    def unsubscribe(self, subscriber):
        super().unsubscribe(subscriber)

    def require(self):
        json_data = self.ExchangeItem.get_json_params()
        response = requests.post(self.trade_url_exchange, json=json_data)
        status_code = response.status_code
        super().handle_status_code(status_code)

        if status_code == 200:
            payload = json.loads(response.text)
            self.subscribers_response['id'] = payload['id']
            self.subscribers_response['complexity'] = payload['complexity']
            self.subscribers_response['result'] = payload['result']
            super().publish()


class GetHandler(RequestHandler, Subscriber, Publisher):
    def __init__(self, ExchangeItem, league):
        super().__init__(ExchangeItem, league)
        self.batch_size = 10
        self.maximum_result_size = 200
        self.request_indexer = []
        self.query_id = None
        self.subscribers = set()
        self.subscribers_response = None

    def publish(self):
        super().publish()

    def subscribe(self, subscriber):
        super().subscribe(subscriber)

    def unsubscribe(self, subscriber):
        super().unsubscribe(subscriber)

    def update(self, *args):
        content = dict(args[0])
        self.query_id = content['id']
        results = content['result']

        if len(results) == self.maximum_result_size:
            self.subscribers_response = {'raise_minimum_stock': True}
            self.publish()

        while len(results) > self.batch_size:
            self.request_indexer.append([results.pop(0)
                                        for x in range(0, self.batch_size)])

        if len(results) > 0:
            self.request_indexer.append(results)

    def require(self):
        for index in self.request_indexer:
            print('Parsing Request')
            items = ','.join(index)
            query = f"{self.trade_url_fetch}{items}?query={self.query_id}"
            response = requests.get(query)
            status_code = response.status_code
            super().handle_status_code(status_code)

            if status_code == 200:
                ep.parse_exchange_response(self.league, response.text)
                self.request_indexer.remove(index)
