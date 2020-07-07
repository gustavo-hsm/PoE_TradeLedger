import requests
import json
from enum import Enum
from Observer import Publisher, Subscriber
from EventType import EventType


class Abs_RequestHandler(Publisher):
    def __init__(self):
        Publisher.__init__(self)
        self.response = None
        self.finished = False
        self.event_type = None

    def is_ready_to_start(self):
        return self.event_type == EventType.HANDLER_READY

    def get_response(self):
        return self.response

    def get_finished(self):
        return self.finished

    def set_response(self, response):
        self.response = response

    def set_finished(self, finished):
        self.finished = finished

    def publish(self, *args):
        super().publish(args)

    def require(self):
        raise NotImplementedError


class PostHandler(Abs_RequestHandler):
    def __init__(self, ExchangeItem, api='exchange'):
        super().__init__()
        self.exchange_item = ExchangeItem
        self.base_url = "https://www.pathofexile.com/api/trade/"
        self.trade_url = {
            'search': self.base_url + 'search/' + self.exchange_item.
            get_league(),
            'exchange': self.base_url + 'exchange/' + self.exchange_item.
            get_league()
        }.get(api, 'exchange')
        self.event_type = EventType.HANDLER_READY

    def publish(self, *args):
        super().publish(args)

    def require(self):
        json_data = self.exchange_item.get_json_params()
        self.event_type = None

        try:
            self.set_response(requests.post(self.trade_url, json=json_data))
            self.event_type = EventType.HANDLER_FINISHED
        except requests.RequestException as e:
            self.event_type = EventType.HANDLER_ERROR
            raise Exception(e)
        finally:
            self.set_finished(True)
            self.publish({
                'event_type': self.event_type,
                'handler': self,
                'exchange_item': self.exchange_item,
                'response_object': self.response
            })


class FetchHandler(Abs_RequestHandler):
    def __init__(self, ExchangeItem, response_object):
        super().__init__()
        self.indexed_queries = []
        self.batch_size = 10
        self.maximum_result_size = 200
        self.base_url = "https://www.pathofexile.com/api/trade/fetch/"
        self.exchange_item = ExchangeItem
        self.response_object = response_object
        self._parse_response_text()

    def publish(self, *args):
        super().publish(args)

    def yield_indexed_query(self):
        for query in self.indexed_queries:
            yield query

    def require(self):
        query_response = []
        event_type = None

        try:
            response = requests.get(next(self.yield_indexed_query()))
            event_type = EventType.HANDLER_NEXT
        except requests.RequestException as e:
            event_type = EventType.HANDLER_ERROR
            raise Exception(e)
        except StopIteration:
            event_type = EventType.HANDLER_FINISHED
            pass
        finally:
            query_response.append(response)
            self.publish({
                'event_type': event_type,
                'handler': self,
                'exchange_item': self.exchange_item,
                'response_object': self.response
            })

    def _parse_response_text(self):
        payload = json.loads(self.response_object.text)
        query_id = payload['id']
        complexity = payload['complexity']
        result = payload['result']

        if len(result) >= self.maximum_result_size:
            self.exchange_item.raise_miminunm_stock()

        items = []
        while len(result) > self.batch_size:
            items.append([result.pop(0) for x in range(0, self.batch_size)])

        if len(result) > 0:
            items.append(result)

        for item in items:
            query = self.base_url + ','.join(item) + '?query=' + query_id
            self.indexed_queries.append(query)
