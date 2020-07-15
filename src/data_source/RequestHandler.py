import requests
import json

from objects.Observer import Publisher
from static.EventType import EventType


class RequestHandler(Publisher):
    def __init__(self, ExchangeItem):
        Publisher.__init__(self)
        self.exchange_item = ExchangeItem
        self.response = None
        self.event_type = None

    def is_ready_to_start(self):
        return self.get_event_type() in (
            EventType.HANDLER_READY, EventType.HANDLER_NEXT)

    def get_exchange_item(self):
        return self.exchange_item

    def get_response(self):
        return self.response

    def get_event_type(self):
        return self.event_type

    def set_response(self, exchange_item):
        self.exchange_item = exchange_item

    def set_response(self, response):
        self.response = response

    def set_event_type(self, event_type):
        self.event_type = event_type

    def publish(self):
        args = {
            'handler': self,
            'event_type': self.get_event_type(),
            'exchange_item': self.get_exchange_item(),
            'response_object': self.get_response()
        }
        super().publish(args)

    def require(self):
        raise NotImplementedError


class PostHandler(RequestHandler):
    def __init__(self, ExchangeItem, api='exchange'):
        super().__init__(ExchangeItem)
        self.base_url = "https://www.pathofexile.com/api/trade/"
        self.trade_url = {
            'search': self.base_url + 'search/' + self.exchange_item.
            get_league(),
            'exchange': self.base_url + 'exchange/' + self.exchange_item.
            get_league()
        }.get(api, 'exchange')
        self.set_event_type(EventType.HANDLER_READY)

    def require(self):
        self.set_event_type(EventType.HANDLER_STARTED)
        json_data = self.exchange_item.get_json_params()

        try:
            self.set_response(requests.post(self.trade_url, json=json_data))
            self.set_event_type(EventType.HANDLER_FINISHED)
        except requests.RequestException as e:
            self.set_event_type(EventType.HANDLER_ERROR)
            raise Exception(e)
        finally:
            self.publish()


class FetchHandler(RequestHandler):
    def __init__(self, ExchangeItem, response_object):
        super().__init__(ExchangeItem)
        self.indexed_queries = []
        self.batch_size = 10
        self.maximum_result_size = 200
        self.base_url = "https://www.pathofexile.com/api/trade/fetch/"
        self.exchange_item = ExchangeItem
        self.response_object = response_object
        self._parse_response_text()
        self.set_event_type(EventType.HANDLER_READY)

    def require(self):
        self.set_event_type(EventType.HANDLER_STARTED)
        try:
            self.set_response(requests.get(self.indexed_queries.pop(0)))
            # Check if this was the last indexed query to require
            if len(self.indexed_queries) == 0:
                self.set_event_type(EventType.HANDLER_FINISHED)
            else:
                self.set_event_type(EventType.HANDLER_NEXT)
        except requests.RequestException as e:
            self.set_event_type(EventType.HANDLER_ERROR)
            raise Exception(e)
        except IndexError:
            self.set_event_type(EventType.HANDLER_FINISHED)
            pass
        finally:
            self.publish()

    def _parse_response_text(self):
        payload = json.loads(self.response_object.text)
        query_id = payload['id']
        complexity = payload['complexity']
        result = payload['result']
        items = []

        if len(result) >= self.maximum_result_size:
            self.exchange_item.raise_minimum_stock()

        while len(result) > self.batch_size:
            items.append([result.pop(0) for x in range(0, self.batch_size)])

        if len(result) > 0:
            items.append(result)

        for item in items:
            query = self.base_url + ','.join(item) + '?query=' + query_id
            self.indexed_queries.append(query)
